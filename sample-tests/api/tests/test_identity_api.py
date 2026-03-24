from __future__ import annotations

import os

import httpx
import pytest


BASE_URL = os.getenv("TARGET_BASE_URL", "http://localhost:8000/api/v1/target-api")


@pytest.mark.contract
def test_identity_permissions_contract() -> None:
    response = httpx.get(f"{BASE_URL}/identity/permissions", timeout=5.0)
    assert response.status_code == 200
    payload = response.json()
    assert payload["tenant"] == "core-platform"
    assert "roles:write" in payload["grants"]


@pytest.mark.contract
def test_mock_order_payload_shape() -> None:
    response = httpx.get(f"{BASE_URL}/orders/CHK-1007", timeout=5.0)
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "confirmed"
    assert payload["line_items"] == 3
