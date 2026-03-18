from __future__ import annotations

from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.db.base import Base


def _engine_options(database_url: str) -> dict:
    if database_url.startswith("sqlite"):
        return {
            "connect_args": {"check_same_thread": False},
        }
    return {
        "pool_pre_ping": True,
    }


@lru_cache
def get_engine() -> AsyncEngine:
    settings = get_settings()
    return create_async_engine(settings.database_url, echo=False, **_engine_options(settings.database_url))


@lru_cache
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(get_engine(), expire_on_commit=False, autoflush=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session


async def init_db() -> None:
    from app import models  # noqa: F401

    async with get_engine().begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def dispose_engine() -> None:
    await get_engine().dispose()
    get_engine.cache_clear()
    get_session_factory.cache_clear()

