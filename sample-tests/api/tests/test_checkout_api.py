from __future__ import annotations

import os

import httpx
import pytest


BASE_URL = os.getenv("TARGET_BASE_URL", "http://localhost:8000/api/v1/target-api")


@pytest.mark.smoke
def test_checkout_session_contract() -> None:
    response = httpx.post(f"{BASE_URL}/auth/session", timeout=5.0)
    assert response.status_code == 200
    payload = response.json()
    assert payload["authenticated"] is True
    assert payload["shopper_id"] == "shopper_1007"


@pytest.mark.smoke
def test_payment_authorization_contract() -> None:
    response = httpx.post(f"{BASE_URL}/payments/authorize", timeout=5.0)
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "authorized"
    assert payload["currency"] == "SEK"
