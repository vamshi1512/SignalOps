from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ApiError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.users import UserRepository
from app.schemas.auth import ProfileUpdate, UserCreate, UserUpdate


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = UserRepository(session)

    async def authenticate(self, email: str, password: str) -> tuple[str, User]:
        user = await self.repository.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise ApiError("invalid_credentials", "Invalid email or password", status_code=401)
        token = create_access_token(user.id, user.role.value)
        return token, user

    async def list_users(self) -> list[User]:
        return await self.repository.list_all()

    async def create_user(self, payload: UserCreate) -> User:
        existing = await self.repository.get_by_email(payload.email)
        if existing:
            raise ApiError("duplicate_user", "A user with that email already exists", status_code=409)
        user = User(
            email=payload.email,
            full_name=payload.full_name,
            title=payload.title,
            password_hash=hash_password(payload.password),
            role=payload.role,
        )
        return await self.repository.add(user)

    async def update_user(self, user_id: str, payload: UserUpdate) -> User:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise ApiError("user_not_found", "User not found", status_code=404)
        for field, value in payload.model_dump(exclude_none=True).items():
            setattr(user, field, value)
        await self.session.flush()
        return user

    async def update_profile(self, user: User, payload: ProfileUpdate) -> User:
        for field, value in payload.model_dump(exclude_none=True).items():
            setattr(user, field, value)
        await self.session.flush()
        return user
