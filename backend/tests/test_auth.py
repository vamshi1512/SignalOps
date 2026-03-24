from __future__ import annotations


async def test_login_and_me(client):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@testforge.dev", "password": "Admin123!"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["user"]["role"] == "admin"

    token = payload["access_token"]
    me_response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "admin@testforge.dev"
