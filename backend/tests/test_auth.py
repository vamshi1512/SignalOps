from __future__ import annotations


async def test_login_and_profile_roundtrip(client):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "ops@roboyard.dev", "password": "Ops123!"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["user"]["role"] == "operator"

    me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {payload['access_token']}"})
    assert me.status_code == 200
    assert me.json()["email"] == "ops@roboyard.dev"


async def test_admin_can_create_user(client, admin_headers):
    response = await client.post(
        "/api/v1/auth/users",
        headers=admin_headers,
        json={
            "email": "new.operator@roboyard.dev",
            "full_name": "New Operator",
            "title": "Shift Commander",
            "password": "Welcome123!",
            "role": "operator",
        },
    )
    assert response.status_code == 200
    assert response.json()["email"] == "new.operator@roboyard.dev"
