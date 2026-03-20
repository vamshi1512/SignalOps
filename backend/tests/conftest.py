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
    db_path = tmp_path / "roboyard-test.db"
    os.environ["ROBOYARD_DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"
    os.environ["ROBOYARD_SEED_ON_START"] = "true"
    os.environ["ROBOYARD_DEMO_MODE"] = "false"
    os.environ["ROBOYARD_METRICS_ENABLED"] = "false"
    get_settings.cache_clear()
    await dispose_engine()

    app = create_app()
    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as test_client:
            yield test_client

    await dispose_engine()
    get_settings.cache_clear()


@pytest.fixture()
async def admin_headers(client: AsyncClient) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@roboyard.dev", "password": "Admin123!"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
async def operator_headers(client: AsyncClient) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "ops@roboyard.dev", "password": "Ops123!"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
async def viewer_headers(client: AsyncClient) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "viewer@roboyard.dev", "password": "Viewer123!"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
