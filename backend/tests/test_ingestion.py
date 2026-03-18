from __future__ import annotations


async def test_log_ingestion_creates_incident(client):
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "sre@signalops.dev", "password": "Sre123!"},
    )
    token = login.json()["access_token"]

    response = await client.post(
        "/api/v1/logs",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "service_slug": "payment-api",
            "severity": "critical",
            "message": "card authorization timeout from upstream gateway",
            "source": "pytest",
            "tags": ["payments", "timeout"],
            "metadata": {"status_code": "504", "region": "eu-north-1"},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["incident_id"] is not None
    assert isinstance(body["alert_ids"], list)

    incidents = await client.get("/api/v1/incidents")
    assert incidents.status_code == 200
    assert incidents.json()["total"] >= 1

