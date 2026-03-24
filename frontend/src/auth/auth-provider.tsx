import {
  createContext,
  type PropsWithChildren,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import { api, ApiError } from "@/lib/api";
import type { AuthSession } from "@/types/api";

const STORAGE_KEY = "testforge-session";

interface AuthContextValue {
  session: AuthSession | null;
  hydrated: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: PropsWithChildren) {
  const validatedTokenRef = useRef<string | null>(null);
  const [session, setSession] = useState<AuthSession | null>(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) {
      return null;
    }
    try {
      return JSON.parse(stored) as AuthSession;
    } catch {
      localStorage.removeItem(STORAGE_KEY);
      return null;
    }
  });
  const [hydrated, setHydrated] = useState(() => !session);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!session) {
      validatedTokenRef.current = null;
      return;
    }
    if (validatedTokenRef.current === session.access_token) {
      return;
    }
    api
      .me(session.access_token)
      .then((user) => {
        validatedTokenRef.current = session.access_token;
        const unchanged =
          session.user.id === user.id &&
          session.user.email === user.email &&
          session.user.full_name === user.full_name &&
          session.user.role === user.role;
        if (!unchanged) {
          const nextSession = { ...session, user };
          setSession(nextSession);
          localStorage.setItem(STORAGE_KEY, JSON.stringify(nextSession));
        }
      })
      .catch(() => {
        validatedTokenRef.current = null;
        setSession(null);
        localStorage.removeItem(STORAGE_KEY);
      })
      .finally(() => setHydrated(true));
  }, [session]);

  async function login(email: string, password: string) {
    setError(null);
    try {
      validatedTokenRef.current = null;
      const nextSession = await api.login(email, password);
      setSession(nextSession);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(nextSession));
    } catch (error) {
      const message =
        error instanceof ApiError ? error.message : "Unable to reach the TestForge API. Check backend availability.";
      setError(message);
      throw error;
    }
  }

  function logout() {
    validatedTokenRef.current = null;
    setSession(null);
    setError(null);
    localStorage.removeItem(STORAGE_KEY);
  }

  const value = useMemo(
    () => ({
      session,
      hydrated,
      error,
      login,
      logout,
      clearError: () => setError(null),
    }),
    [error, hydrated, session],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
