from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ApiError
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.repositories.users import UserRepository


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = UserRepository(session)

    async def authenticate(self, email: str, password: str) -> tuple[str, User]:
        user = await self.repository.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise ApiError("invalid_credentials", "Invalid email or password", status_code=401)
        token = create_access_token(user.id, user.role.value)
        return token, user

