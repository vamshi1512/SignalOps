from __future__ import annotations


async def test_dashboard_overview_returns_metrics(client):
    response = await client.get("/api/v1/dashboard/overview")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["metrics"]) >= 5
    assert len(payload["services"]) >= 3
    assert "incident_trend" in payload
