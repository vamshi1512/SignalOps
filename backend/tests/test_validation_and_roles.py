from __future__ import annotations


async def test_viewer_cannot_access_admin_config(client, viewer_headers):
    response = await client.get("/api/v1/config", headers=viewer_headers)
    assert response.status_code == 403


async def test_create_mission_rejects_invalid_schedule(client, operator_headers):
    robots_response = await client.get("/api/v1/fleet/robots", headers=operator_headers)
    robot = robots_response.json()["items"][0]

    response = await client.post(
        "/api/v1/missions",
        headers=operator_headers,
        json={
            "robot_id": robot["id"],
            "zone_id": robot["zone"]["id"],
            "name": "Invalid schedule",
            "mission_type": "mow",
            "scheduled_start": "2026-03-20T10:00:00Z",
            "scheduled_end": "2026-03-20T09:00:00Z",
            "target_area_sqm": 480,
        },
    )
    assert response.status_code == 422


async def test_create_mission_rejects_existing_active_lane(client, operator_headers):
    robots_response = await client.get("/api/v1/fleet/robots", headers=operator_headers)
    robot = robots_response.json()["items"][0]

    response = await client.post(
        "/api/v1/missions",
        headers=operator_headers,
        json={
            "robot_id": robot["id"],
            "zone_id": robot["zone"]["id"],
            "name": "Overlap lane",
            "mission_type": "mow",
            "target_area_sqm": 510,
        },
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "mission_conflict"
