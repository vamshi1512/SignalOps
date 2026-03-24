from __future__ import annotations


async def test_catalog_endpoints_return_seeded_inventory(client, auth_headers):
    projects = await client.get("/api/v1/projects", headers=auth_headers)
    assert projects.status_code == 200
    assert projects.json()["total"] >= 2

    environments = await client.get("/api/v1/environments", headers=auth_headers)
    assert environments.status_code == 200
    assert any(item["kind"] == "staging" for item in environments.json()["items"])
    assert any(item["status"] == "offline" for item in environments.json()["items"])

    suites = await client.get("/api/v1/suites", headers=auth_headers)
    assert suites.status_code == 200
    assert any(item["suite_type"] == "api" for item in suites.json()["items"])
    assert any(item["suite_type"] == "ui" for item in suites.json()["items"])

    schedules = await client.get("/api/v1/schedules", headers=auth_headers)
    assert schedules.status_code == 200
    assert schedules.json()["total"] >= 4


async def test_schedule_patch_requires_a_field(client, auth_headers):
    schedules = await client.get("/api/v1/schedules", headers=auth_headers)
    schedule = schedules.json()["items"][0]

    response = await client.patch(
        f"/api/v1/schedules/{schedule['id']}",
        headers=auth_headers,
        json={},
    )

    assert response.status_code == 422
