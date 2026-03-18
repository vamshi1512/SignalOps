from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: str) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[User]:
        result = await self.session.execute(select(User).order_by(User.full_name))
        return list(result.scalars().all())

    async def add(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        return user

