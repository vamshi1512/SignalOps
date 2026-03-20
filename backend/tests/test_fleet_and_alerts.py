from __future__ import annotations


async def test_robot_listing_and_command_flow(client, operator_headers):
    robots_response = await client.get("/api/v1/fleet/robots", headers=operator_headers)
    assert robots_response.status_code == 200
    robots = robots_response.json()["items"]
    robot_id = robots[0]["id"]

    command_response = await client.post(
        f"/api/v1/missions/robots/{robot_id}/commands",
        headers=operator_headers,
        json={"command": "pause", "note": "Operator pause for inspection"},
    )
    assert command_response.status_code == 200
    assert command_response.json()["status"] == "paused"


async def test_alert_acknowledgement(client, operator_headers):
    alerts_response = await client.get("/api/v1/alerts", headers=operator_headers)
    assert alerts_response.status_code == 200
    alerts = alerts_response.json()["items"]
    open_alert = next(item for item in alerts if item["status"] == "open")

    ack_response = await client.post(
        f"/api/v1/alerts/{open_alert['id']}/acknowledge",
        headers=operator_headers,
        json={"notes": "Acknowledged from test"},
    )
    assert ack_response.status_code == 200
    assert ack_response.json()["status"] == "acknowledged"
