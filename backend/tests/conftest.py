from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.db.session import dispose_engine
from app.main import create_app


@pytest.fixture()
async def client(tmp_path) -> AsyncIterator[AsyncClient]:
    db_path = tmp_path / "signalops-test.db"
    os.environ["SIGNALOPS_DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"
    os.environ["SIGNALOPS_SEED_ON_START"] = "true"
    os.environ["SIGNALOPS_METRICS_ENABLED"] = "false"
    get_settings.cache_clear()
    await dispose_engine()

    app = create_app()
    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as test_client:
            yield test_client

    await dispose_engine()
    get_settings.cache_clear()

