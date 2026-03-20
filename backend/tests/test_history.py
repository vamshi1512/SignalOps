from __future__ import annotations


async def test_robot_history_and_replay(client, operator_headers):
    robots_response = await client.get("/api/v1/fleet/robots", headers=operator_headers)
    robot = robots_response.json()["items"][0]

    history_response = await client.get(f"/api/v1/history/robots/{robot['id']}", headers=operator_headers)
    assert history_response.status_code == 200
    history_payload = history_response.json()
    assert history_payload["telemetry"]
    assert history_payload["missions"]

    mission_id = history_payload["missions"][0]["id"]
    replay_response = await client.get(f"/api/v1/history/missions/{mission_id}/replay", headers=operator_headers)
    assert replay_response.status_code == 200
    assert replay_response.json()["telemetry"]
