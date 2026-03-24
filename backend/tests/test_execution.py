from __future__ import annotations


async def test_launching_ui_suite_generates_failure_artifacts_and_notifications(client, auth_headers):
    suites = await client.get("/api/v1/suites", headers=auth_headers)
    assert suites.status_code == 200
    suite = next(item for item in suites.json()["items"] if item["slug"] == "checkout-ui-journeys")

    launch = await client.post(
        f"/api/v1/suites/{suite['id']}/runs",
        headers=auth_headers,
        json={},
    )
    assert launch.status_code == 200
    run_id = launch.json()["id"]

    run_detail = await client.get(f"/api/v1/runs/{run_id}", headers=auth_headers)
    assert run_detail.status_code == 200
    payload = run_detail.json()
    assert payload["status"] == "failed"
    assert payload["fail_count"] >= 1
    assert any(
        attachment["type"] == "image"
        for result in payload["results"]
        for attachment in result["attachments"]
    )

    notifications = await client.get("/api/v1/notifications", headers=auth_headers)
    assert notifications.status_code == 200
    assert notifications.json()["total"] >= 1


async def test_manual_run_rejects_cross_project_environment(client, auth_headers):
    suites = await client.get("/api/v1/suites", headers=auth_headers)
    environments = await client.get("/api/v1/environments", headers=auth_headers)

    checkout_suite = next(item for item in suites.json()["items"] if item["slug"] == "checkout-ui-journeys")
    identity_environment = next(item for item in environments.json()["items"] if item["slug"] == "identity-qa")

    launch = await client.post(
        f"/api/v1/suites/{checkout_suite['id']}/runs",
        headers=auth_headers,
        json={"environment_id": identity_environment["id"]},
    )

    assert launch.status_code == 400
    assert launch.json()["error"]["code"] == "environment_project_mismatch"


async def test_run_duration_includes_execution_overhead_and_metadata(client, auth_headers):
    suites = await client.get("/api/v1/suites", headers=auth_headers)
    suite = next(item for item in suites.json()["items"] if item["slug"] == "checkout-api-regression")

    launch = await client.post(
        f"/api/v1/suites/{suite['id']}/runs",
        headers=auth_headers,
        json={},
    )
    assert launch.status_code == 200

    payload = launch.json()
    result_duration_total = sum(result["duration_ms"] for result in (await client.get(f"/api/v1/runs/{payload['id']}", headers=auth_headers)).json()["results"])

    assert payload["duration_ms"] > result_duration_total
    assert payload["metadata"]["runner"] == "deterministic-simulator"
