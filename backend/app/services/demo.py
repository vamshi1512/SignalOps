from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.enums import EnvironmentKind, EnvironmentStatus, SuiteStatus, SuiteType, TriggerType, UserRole
from app.models.qa import Environment, FixtureSet, Project, RunSchedule, TestCase, TestSuite
from app.models.user import User
from app.repositories.users import UserRepository
from app.services.execution import ExecutionService


USERS = [
    ("admin@testforge.dev", "TestForge Admin", "Admin123!", UserRole.ADMIN),
    ("qa.lead@testforge.dev", "QA Lead", "QaLead123!", UserRole.QA_ENGINEER),
    ("viewer@testforge.dev", "Read Only Viewer", "Viewer123!", UserRole.VIEWER),
]

PROJECTS = [
    {
        "name": "Checkout Core",
        "slug": "checkout-core",
        "owner": "Team Helix",
        "repository_url": "https://github.com/example/testforge-checkout-core",
        "default_branch": "release/2026.03",
        "description": "Cross-channel checkout coverage with contract checks, visual confidence gates, and release-day smoke automation.",
    },
    {
        "name": "Identity Edge",
        "slug": "identity-edge",
        "owner": "Team Atlas",
        "repository_url": "https://github.com/example/testforge-identity-edge",
        "default_branch": "main",
        "description": "Authentication, admin RBAC, and audit workflows with seeded tenant personas and release-health verification.",
    },
]


class DemoService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.execution = ExecutionService(session)

    async def seed(self) -> None:
        if await self.users.get_by_email("admin@testforge.dev"):
            return

        for email, full_name, password, role in USERS:
            await self.users.add(
                User(
                    email=email,
                    full_name=full_name,
                    password_hash=hash_password(password),
                    role=role,
                )
            )

        projects: dict[str, Project] = {}
        for definition in PROJECTS:
            project = Project(**definition)
            self.session.add(project)
            await self.session.flush()
            projects[project.slug] = project

        environments = await self._seed_environments(projects)
        fixtures = await self._seed_fixture_sets(projects)
        suites = await self._seed_suites(projects, environments, fixtures)
        schedules = await self._seed_schedules(suites, environments)
        await self._seed_run_history(schedules)

    async def _seed_environments(self, projects: dict[str, Project]) -> dict[str, Environment]:
        base_api = "http://backend:8000/api/v1"
        base_ui = "http://backend:8000/api/v1"
        definitions = [
            ("checkout-core", "Checkout QA", "checkout-qa", EnvironmentKind.QA, EnvironmentStatus.HEALTHY, True, "Primary merge-train validation lane."),
            ("checkout-core", "Checkout Staging", "checkout-staging", EnvironmentKind.STAGING, EnvironmentStatus.HEALTHY, False, "Release-candidate environment with payment gateway replay."),
            ("checkout-core", "Checkout Prod-like Mock", "checkout-prod-like", EnvironmentKind.PROD_LIKE, EnvironmentStatus.HEALTHY, False, "Synthetic prod-like traffic replay for release rehearsals."),
            ("checkout-core", "Checkout Sandbox", "checkout-sandbox", EnvironmentKind.MOCK, EnvironmentStatus.OFFLINE, False, "Sandbox target reserved for exploratory fixture authoring."),
            ("identity-edge", "Identity QA", "identity-qa", EnvironmentKind.QA, EnvironmentStatus.HEALTHY, True, "Tenant RBAC validation against the QA control plane."),
            ("identity-edge", "Identity Staging", "identity-staging", EnvironmentKind.STAGING, EnvironmentStatus.DEGRADED, False, "Staging sync lag detected in upstream directory mirror."),
            ("identity-edge", "Identity Mock", "identity-mock", EnvironmentKind.MOCK, EnvironmentStatus.HEALTHY, False, "Mock admin portal used for deterministic UI suite playback."),
        ]
        environments: dict[str, Environment] = {}
        for project_slug, name, slug, kind, status, is_default, health_summary in definitions:
            project_code = project_slug.replace("-", "_").upper()
            environment = Environment(
                project_id=projects[project_slug].id,
                name=name,
                slug=slug,
                kind=kind,
                status=status,
                api_base_url=base_api,
                ui_base_url=base_ui,
                health_summary=health_summary,
                variables={
                    "RELEASE_RING": "2026.03",
                    "BROWSER": "chromium",
                    "REGION": "eu-north-1",
                    "PROJECT_CODE": project_code,
                },
                is_default=is_default,
            )
            self.session.add(environment)
            await self.session.flush()
            environments[slug] = environment
        return environments

    async def _seed_fixture_sets(self, projects: dict[str, Project]) -> dict[str, FixtureSet]:
        definitions = [
            (
                "checkout-core",
                "shopper-persona-seed",
                "Shopper Persona Seed",
                "Baseline carts, stored cards, shipping addresses, and tax fixtures for checkout execution.",
                {
                    "currency": "SEK",
                    "locale": "sv-SE",
                    "cart_items": 3,
                    "payment_method": "visa",
                    "shopper": {"segment": "returning", "loyalty_tier": "gold"},
                },
            ),
            (
                "checkout-core",
                "payment-retry-matrix",
                "Payment Retry Matrix",
                "Retry and timeout scenarios for gateway and reconciliation checks.",
                {
                    "gateway_outcomes": ["200", "200", "503"],
                    "retry_budget": 2,
                    "fallback_acquirer": "mockpay-secondary",
                    "timeouts_ms": [850, 1200, 2400],
                },
            ),
            (
                "identity-edge",
                "role-sync-dataset",
                "Role Sync Dataset",
                "Seeded admin, operator, and auditor identities for auth regression.",
                {
                    "roles": ["admin", "operator", "auditor"],
                    "tenants": 4,
                    "directory_snapshot": "2026-03-19T08:00:00Z",
                    "feature_flags": {"scim_sync": True, "jit_provisioning": False},
                },
            ),
        ]
        fixtures: dict[str, FixtureSet] = {}
        for project_slug, slug, name, description, payload in definitions:
            fixture_set = FixtureSet(
                project_id=projects[project_slug].id,
                name=name,
                description=description,
                payload=payload,
            )
            self.session.add(fixture_set)
            await self.session.flush()
            fixtures[slug] = fixture_set
        return fixtures

    async def _seed_suites(
        self,
        projects: dict[str, Project],
        environments: dict[str, Environment],
        fixtures: dict[str, FixtureSet],
    ) -> dict[str, TestSuite]:
        suite_definitions = [
            {
                "slug": "checkout-api-regression",
                "project_slug": "checkout-core",
                "default_environment_slug": "checkout-qa",
                "default_fixture_slug": "shopper-persona-seed",
                "name": "Checkout API Regression",
                "suite_type": SuiteType.API,
                "owner": "Team Helix",
                "description": "Critical API contracts for session hydration, order totals, and payment authorization.",
                "repo_path": "sample-tests/api/tests/test_checkout_api.py",
                "command": "pytest sample-tests/api/tests/test_checkout_api.py -m smoke",
                "tags": ["api", "smoke", "checkout"],
                "parallel_workers": 4,
                "status": SuiteStatus.ACTIVE,
                "is_flaky_watch": True,
                "cases": [
                    ("checkout.api.session", "checkout-api-session", "Hydrates checkout session", "stable", 900, ["api", "session"]),
                    ("payment.authorize", "checkout-api-payment", "Authorizes payment intent", "flaky", 1100, ["api", "payments"]),
                    ("orders.summary", "checkout-api-order-summary", "Validates order summary contract", "staging-risk", 980, ["api", "orders"]),
                    ("checkout.api.cart", "checkout-api-cart", "Recomputes cart totals", "slow-burn", 1240, ["api", "cart"]),
                ],
            },
            {
                "slug": "checkout-ui-journeys",
                "project_slug": "checkout-core",
                "default_environment_slug": "checkout-staging",
                "default_fixture_slug": "shopper-persona-seed",
                "name": "Checkout UI Journeys",
                "suite_type": SuiteType.UI,
                "owner": "Team Helix",
                "description": "Browser smoke coverage for sign-in, shipping, payment, and receipt rendering.",
                "repo_path": "sample-tests/ui/tests/checkout-journey.spec.ts",
                "command": "npx playwright test sample-tests/ui/tests/checkout-journey.spec.ts",
                "tags": ["ui", "critical-path", "checkout"],
                "parallel_workers": 2,
                "status": SuiteStatus.ACTIVE,
                "is_flaky_watch": True,
                "cases": [
                    ("checkout.ui.login", "checkout-ui-login", "Signs in returning shopper", "stable", 1600, ["ui", "auth"]),
                    ("checkout.ui.confirmation", "checkout-ui-confirmation", "Completes checkout confirmation", "ui-visual", 1900, ["ui", "checkout"]),
                    ("checkout.ui.promo", "checkout-ui-promo", "Applies promo banner discount", "flaky", 1550, ["ui", "promo"]),
                    ("checkout.ui.receipt", "checkout-ui-receipt", "Renders receipt totals", "stable", 1450, ["ui", "receipt"]),
                ],
            },
            {
                "slug": "identity-api-contract",
                "project_slug": "identity-edge",
                "default_environment_slug": "identity-qa",
                "default_fixture_slug": "role-sync-dataset",
                "name": "Identity API Contract",
                "suite_type": SuiteType.API,
                "owner": "Team Atlas",
                "description": "Auth contract and RBAC permission validation across tenant and admin APIs.",
                "repo_path": "sample-tests/api/tests/test_identity_api.py",
                "command": "pytest sample-tests/api/tests/test_identity_api.py -m contract",
                "tags": ["api", "contract", "identity"],
                "parallel_workers": 3,
                "status": SuiteStatus.ACTIVE,
                "is_flaky_watch": False,
                "cases": [
                    ("identity.permissions", "identity-api-permissions", "Returns tenant permission matrix", "stable", 840, ["api", "identity"]),
                    ("identity.session", "identity-api-session", "Renews admin session token", "stable", 780, ["api", "auth"]),
                    ("identity.directory", "identity-api-directory", "Syncs operator directory delta", "contract-drift", 1010, ["api", "directory"]),
                    ("identity.audit", "identity-api-audit", "Streams audit records", "slow-burn", 1180, ["api", "audit"]),
                ],
            },
            {
                "slug": "admin-portal-ui-smoke",
                "project_slug": "identity-edge",
                "default_environment_slug": "identity-mock",
                "default_fixture_slug": "role-sync-dataset",
                "name": "Admin Portal UI Smoke",
                "suite_type": SuiteType.UI,
                "owner": "Team Atlas",
                "description": "Admin portal smoke coverage for login, role review, and audit table interactions.",
                "repo_path": "sample-tests/ui/tests/admin-portal.spec.ts",
                "command": "npx playwright test sample-tests/ui/tests/admin-portal.spec.ts",
                "tags": ["ui", "smoke", "identity"],
                "parallel_workers": 2,
                "status": SuiteStatus.ACTIVE,
                "is_flaky_watch": True,
                "cases": [
                    ("admin.ui.login", "admin-ui-login", "Logs into admin portal", "stable", 1300, ["ui", "auth"]),
                    ("admin.ui.roles", "admin-ui-roles", "Reviews role sync banner", "flaky", 1420, ["ui", "roles"]),
                    ("admin.ui.audit", "admin-ui-audit", "Opens audit drawer", "ui-visual", 1710, ["ui", "audit"]),
                    ("admin.ui.tenant", "admin-ui-tenant", "Switches tenant context", "stable", 1380, ["ui", "tenant"]),
                ],
            },
        ]
        suites: dict[str, TestSuite] = {}
        for definition in suite_definitions:
            suite = TestSuite(
                project_id=projects[definition["project_slug"]].id,
                default_environment_id=environments[definition["default_environment_slug"]].id,
                default_fixture_set_id=fixtures[definition["default_fixture_slug"]].id,
                name=definition["name"],
                slug=definition["slug"],
                suite_type=definition["suite_type"],
                owner=definition["owner"],
                description=definition["description"],
                repo_path=definition["repo_path"],
                command=definition["command"],
                tags=definition["tags"],
                parallel_workers=definition["parallel_workers"],
                status=definition["status"],
                is_flaky_watch=definition["is_flaky_watch"],
            )
            self.session.add(suite)
            await self.session.flush()
            suites[definition["slug"]] = suite
            for index, (module_name, case_key, name, profile, baseline, tags) in enumerate(definition["cases"], start=1):
                self.session.add(
                    TestCase(
                        suite_id=suite.id,
                        key=case_key,
                        name=name,
                        module_name=module_name,
                        order_index=index,
                        automation_ref=f"{definition['repo_path']}::{case_key}",
                        expected_outcome="Stable green path against seeded target routes.",
                        deterministic_profile=profile,
                        baseline_duration_ms=baseline,
                        tags=tags,
                        fixture_overrides={"dataset": definition["default_fixture_slug"]},
                    )
                )
        await self.session.flush()
        return suites

    async def _seed_schedules(self, suites: dict[str, TestSuite], environments: dict[str, Environment]) -> list[RunSchedule]:
        schedule_definitions = [
            ("checkout-api-regression", "checkout-qa", "Checkout API smoke cadence", 120, 4),
            ("checkout-ui-journeys", "checkout-staging", "Checkout UI release cadence", 180, 2),
            ("identity-api-contract", "identity-qa", "Identity API contract cadence", 90, 3),
            ("admin-portal-ui-smoke", "identity-mock", "Admin smoke cadence", 240, 2),
        ]
        now = datetime.now(timezone.utc)
        schedules: list[RunSchedule] = []
        for suite_slug, environment_slug, name, cadence_minutes, parallel_workers in schedule_definitions:
            schedule = RunSchedule(
                suite_id=suites[suite_slug].id,
                environment_id=environments[environment_slug].id,
                name=name,
                cadence_minutes=cadence_minutes,
                next_run_at=now + timedelta(minutes=max(cadence_minutes // 3, 20)),
                last_run_at=None,
                parallel_workers=parallel_workers,
                timezone="Europe/Stockholm",
                active=True,
            )
            self.session.add(schedule)
            schedules.append(schedule)
        await self.session.flush()
        return schedules

    async def _seed_run_history(self, schedules: list[RunSchedule]) -> None:
        admin = await self.users.get_by_email("admin@testforge.dev")
        qa_lead = await self.users.get_by_email("qa.lead@testforge.dev")
        now = datetime.now(timezone.utc)
        for schedule in schedules:
            for ordinal in range(8, 0, -1):
                started_at = now - timedelta(minutes=schedule.cadence_minutes * ordinal)
                run = await self.execution.create_run_for_suite(
                    schedule.suite_id,
                    trigger_type=TriggerType.SCHEDULED,
                    environment_id=schedule.environment_id,
                    schedule_id=schedule.id,
                    parallel_workers=schedule.parallel_workers,
                    created_at=started_at - timedelta(minutes=3),
                )
                await self.execution.execute_run(run.id, started_at=started_at)
                schedule.last_run_at = started_at

        manual_target = schedules[1]
        manual_run = await self.execution.create_run_for_suite(
            manual_target.suite_id,
            trigger_type=TriggerType.MANUAL,
            actor=admin,
            environment_id=manual_target.environment_id,
            schedule_id=None,
            parallel_workers=manual_target.parallel_workers,
            created_at=now - timedelta(minutes=25),
        )
        await self.execution.execute_run(manual_run.id, started_at=now - timedelta(minutes=22))

        api_manual_target = schedules[2]
        api_manual_run = await self.execution.create_run_for_suite(
            api_manual_target.suite_id,
            trigger_type=TriggerType.MANUAL,
            actor=qa_lead,
            environment_id=api_manual_target.environment_id,
            fixture_set_id=None,
            schedule_id=None,
            parallel_workers=api_manual_target.parallel_workers,
            created_at=now - timedelta(hours=3, minutes=18),
        )
        await self.execution.execute_run(api_manual_run.id, started_at=now - timedelta(hours=3, minutes=14))

        demo_target = schedules[0]
        demo_run = await self.execution.create_run_for_suite(
            demo_target.suite_id,
            trigger_type=TriggerType.DEMO,
            actor=admin,
            environment_id=demo_target.environment_id,
            fixture_set_id=None,
            schedule_id=None,
            parallel_workers=max(demo_target.parallel_workers - 1, 1),
            created_at=now - timedelta(hours=6, minutes=9),
        )
        await self.execution.execute_run(demo_run.id, started_at=now - timedelta(hours=6, minutes=5))

        result = await self.session.execute(select(RunSchedule))
        for schedule in result.scalars().all():
            if schedule.last_run_at:
                schedule.next_run_at = schedule.last_run_at + timedelta(minutes=schedule.cadence_minutes)
