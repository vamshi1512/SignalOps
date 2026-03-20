from __future__ import annotations


async def test_dashboard_overview_has_seeded_fleet(client, operator_headers):
    response = await client.get("/api/v1/dashboard/overview", headers=operator_headers)
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["robots"]) >= 6
    assert len(payload["zones"]) >= 3
    assert payload["metrics"][0]["label"] == "Live Robots"
    assert payload["weather"]["state"] in {"clear", "drizzle", "rain", "wind_gust", "storm"}
