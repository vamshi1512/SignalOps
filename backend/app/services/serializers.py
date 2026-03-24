from __future__ import annotations

from typing import Any

from app.models.audit import AuditLog
from app.models.qa import Environment, FixtureSet, NotificationEvent, Project, RunSchedule, TestCase, TestResult, TestRun, TestSuite
from app.models.user import User


def serialize_user(user: User | None) -> dict[str, Any] | None:
    if not user:
        return None
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
    }


def serialize_project(project: Project) -> dict[str, Any]:
    return {
        "id": project.id,
        "name": project.name,
        "slug": project.slug,
        "owner": project.owner,
        "repository_url": project.repository_url,
        "default_branch": project.default_branch,
        "description": project.description,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
    }


def serialize_environment(environment: Environment) -> dict[str, Any]:
    return {
        "id": environment.id,
        "project_id": environment.project_id,
        "name": environment.name,
        "slug": environment.slug,
        "kind": environment.kind,
        "status": environment.status,
        "api_base_url": environment.api_base_url,
        "ui_base_url": environment.ui_base_url,
        "health_summary": environment.health_summary,
        "variables": environment.variables,
        "is_default": environment.is_default,
        "last_checked_at": environment.last_checked_at,
        "created_at": environment.created_at,
        "updated_at": environment.updated_at,
    }


def serialize_fixture_set(fixture_set: FixtureSet | None) -> dict[str, Any] | None:
    if not fixture_set:
        return None
    return {
        "id": fixture_set.id,
        "project_id": fixture_set.project_id,
        "name": fixture_set.name,
        "description": fixture_set.description,
        "payload": fixture_set.payload,
        "created_at": fixture_set.created_at,
        "updated_at": fixture_set.updated_at,
    }


def serialize_test_case(test_case: TestCase) -> dict[str, Any]:
    return {
        "id": test_case.id,
        "key": test_case.key,
        "name": test_case.name,
        "module_name": test_case.module_name,
        "order_index": test_case.order_index,
        "automation_ref": test_case.automation_ref,
        "expected_outcome": test_case.expected_outcome,
        "deterministic_profile": test_case.deterministic_profile,
        "baseline_duration_ms": test_case.baseline_duration_ms,
        "tags": test_case.tags,
        "fixture_overrides": test_case.fixture_overrides,
    }


def serialize_schedule(schedule: RunSchedule | None) -> dict[str, Any] | None:
    if not schedule:
        return None
    environment_name = schedule.environment.name if schedule.environment else ""
    return {
        "id": schedule.id,
        "suite_id": schedule.suite_id,
        "environment_id": schedule.environment_id,
        "name": schedule.name,
        "cadence_minutes": schedule.cadence_minutes,
        "next_run_at": schedule.next_run_at,
        "last_run_at": schedule.last_run_at,
        "parallel_workers": schedule.parallel_workers,
        "timezone": schedule.timezone,
        "active": schedule.active,
        "environment_name": environment_name,
    }


def serialize_suite_summary(suite: TestSuite) -> dict[str, Any]:
    return {
        "id": suite.id,
        "name": suite.name,
        "slug": suite.slug,
        "suite_type": suite.suite_type,
        "owner": suite.owner,
        "tags": suite.tags,
        "status": suite.status,
    }


def serialize_suite(
    suite: TestSuite,
    *,
    latest_run_status: Any = None,
    last_run_at: Any = None,
    pass_rate_14d: float = 0.0,
    flaky_cases: int = 0,
) -> dict[str, Any]:
    return {
        **serialize_suite_summary(suite),
        "description": suite.description,
        "repo_path": suite.repo_path,
        "command": suite.command,
        "parallel_workers": suite.parallel_workers,
        "is_flaky_watch": suite.is_flaky_watch,
        "created_at": suite.created_at,
        "updated_at": suite.updated_at,
        "project": serialize_project(suite.project),
        "default_environment": serialize_environment(suite.default_environment) if suite.default_environment else None,
        "default_fixture_set": serialize_fixture_set(suite.default_fixture_set),
        "test_cases": [serialize_test_case(test_case) for test_case in suite.test_cases],
        "schedules": [serialize_schedule(schedule) for schedule in suite.schedules],
        "latest_run_status": latest_run_status,
        "last_run_at": last_run_at,
        "pass_rate_14d": pass_rate_14d,
        "flaky_cases": flaky_cases,
    }


def serialize_notification(notification: NotificationEvent) -> dict[str, Any]:
    return {
        "id": notification.id,
        "channel": notification.channel,
        "status": notification.status,
        "recipient": notification.recipient,
        "subject": notification.subject,
        "message": notification.message,
        "delivered_at": notification.delivered_at,
        "metadata": notification.payload,
        "created_at": notification.created_at,
    }


def serialize_result(result: TestResult) -> dict[str, Any]:
    return {
        "id": result.id,
        "test_case_id": result.test_case_id,
        "name": result.name,
        "module_name": result.module_name,
        "status": result.status,
        "retry_count": result.retry_count,
        "is_flaky": result.is_flaky,
        "duration_ms": result.duration_ms,
        "started_at": result.started_at,
        "finished_at": result.finished_at,
        "error_message": result.error_message,
        "stack_trace": result.stack_trace,
        "logs": result.logs,
        "request_details": result.request_details,
        "response_details": result.response_details,
        "attachments": result.attachments,
    }


def serialize_run(run: TestRun, *, include_results: bool = False) -> dict[str, Any]:
    payload = {
        "id": run.id,
        "trigger_type": run.trigger_type,
        "status": run.status,
        "requested_parallel_workers": run.requested_parallel_workers,
        "total_count": run.total_count,
        "pass_count": run.pass_count,
        "fail_count": run.fail_count,
        "skip_count": run.skip_count,
        "flaky_count": run.flaky_count,
        "duration_ms": run.duration_ms,
        "started_at": run.started_at,
        "finished_at": run.finished_at,
        "created_at": run.created_at,
        "summary": run.summary,
        "metadata": run.runtime_metadata,
        "project": serialize_project(run.project),
        "suite": serialize_suite_summary(run.suite),
        "environment": serialize_environment(run.environment),
        "fixture_set": serialize_fixture_set(run.fixture_set),
        "schedule": serialize_schedule(run.schedule),
        "triggered_by": serialize_user(run.triggered_by),
    }
    if include_results:
        payload["results"] = [serialize_result(result) for result in run.results]
        payload["notifications"] = [serialize_notification(notification) for notification in run.notifications]
    return payload


def serialize_audit_entry(entry: AuditLog) -> dict[str, Any]:
    return {
        "id": entry.id,
        "actor_id": entry.actor_id,
        "actor_email": entry.actor_email,
        "action": entry.action,
        "resource_type": entry.resource_type,
        "resource_id": entry.resource_id,
        "details": entry.details,
        "created_at": entry.created_at,
        "message": entry.message,
    }
