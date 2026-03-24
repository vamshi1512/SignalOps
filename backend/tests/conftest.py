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
    db_path = tmp_path / "testforge-test.db"
    artifact_path = tmp_path / "artifacts"
    os.environ["TESTFORGE_DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"
    os.environ["TESTFORGE_ARTIFACT_ROOT"] = str(artifact_path)
    os.environ["TESTFORGE_SEED_ON_START"] = "true"
    os.environ["TESTFORGE_METRICS_ENABLED"] = "false"
    os.environ["TESTFORGE_CELERY_EAGER"] = "true"
    get_settings.cache_clear()
    await dispose_engine()

    app = create_app()
    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as test_client:
            yield test_client

    await dispose_engine()
    get_settings.cache_clear()


@pytest.fixture()
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "qa.lead@testforge.dev", "password": "QaLead123!"},
    )
    payload = response.json()
    return {"Authorization": f"Bearer {payload['access_token']}"}
