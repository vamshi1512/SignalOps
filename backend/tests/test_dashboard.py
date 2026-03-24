from __future__ import annotations


async def test_dashboard_overview_returns_metrics(client, auth_headers):
    response = await client.get("/api/v1/dashboard/overview", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["metrics"]) >= 5
    assert len(payload["recent_runs"]) >= 4
    assert len(payload["suites_at_risk"]) >= 1
    assert "pass_rate_trend" in payload
    assert any(item["status"] in {"degraded", "offline"} for item in payload["environments"])
