from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.session import get_session
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.users import UserRepository


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    authorization: str | None = Header(default=None),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    return await get_user_from_token(authorization.replace("Bearer ", "", 1), session)


async def get_user_from_token(token: str, session: AsyncSession) -> User:
    try:
        payload = decode_token(token)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    user = await UserRepository(session).get_by_id(payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User unavailable")
    return user


def require_roles(*roles: UserRole) -> Callable[[User], User]:
    async def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return dependency


def get_simulator(request: Request):
    return request.app.state.simulator
