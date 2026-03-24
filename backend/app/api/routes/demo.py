from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter()


@router.get("/demo/targets")
async def demo_targets() -> dict:
    return {
        "api_base": "/api/v1/target-api",
        "ui_base": "/api/v1/target-ui",
        "sample_commands": {
            "api": "pytest sample-tests/api/tests/test_checkout_api.py -m smoke",
            "ui": "npx playwright test sample-tests/ui/tests/checkout-journey.spec.ts",
        },
    }


@router.get("/target-api/health")
async def target_api_health() -> dict:
    return {
        "status": "ok",
        "release": "2026.03.24-rc1",
        "region": "eu-north-1",
        "synthetic_dependencies": {"payments": "healthy", "identity": "healthy", "inventory": "degraded"},
    }


@router.post("/target-api/auth/session")
async def target_auth_session() -> dict:
    return {
        "session_id": "sess_demo_qa_001",
        "shopper_id": "shopper_1007",
        "tenant": "nordics",
        "authenticated": True,
    }


@router.post("/target-api/payments/authorize")
async def target_payment_authorize() -> dict:
    return {
        "authorization_id": "auth_424242",
        "status": "authorized",
        "gateway": "mockpay",
        "amount": 9900,
        "currency": "SEK",
    }


@router.get("/target-api/orders/{order_id}")
async def target_order(order_id: str) -> dict:
    return {
        "order_id": order_id,
        "status": "confirmed",
        "total_minor": 9900,
        "currency": "SEK",
        "line_items": 3,
    }


@router.get("/target-api/identity/permissions")
async def target_permissions() -> dict:
    return {
        "tenant": "core-platform",
        "roles": ["admin", "operator", "auditor"],
        "grants": ["users:read", "roles:write", "audit:read"],
    }


@router.get("/target-ui/checkout", response_class=HTMLResponse)
async def target_checkout_ui() -> str:
    return """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>TestForge Checkout Mock</title>
    <style>
      :root { color-scheme: dark; }
      * { box-sizing: border-box; }
      body {
        font-family: "IBM Plex Sans", system-ui, sans-serif;
        background:
          radial-gradient(circle at top left, rgba(56, 189, 248, 0.18), transparent 28%),
          radial-gradient(circle at top right, rgba(251, 146, 60, 0.14), transparent 24%),
          linear-gradient(180deg, #081120, #050b16);
        color: #e2e8f0;
        margin: 0;
        min-height: 100vh;
        padding: 40px;
      }
      .card {
        max-width: 980px;
        margin: 0 auto;
        background: rgba(15, 23, 42, 0.92);
        border: 1px solid rgba(56, 189, 248, 0.16);
        border-radius: 32px;
        padding: 36px;
        box-shadow: 0 32px 80px rgba(2, 6, 23, 0.45);
      }
      .eyebrow {
        display: inline-flex;
        border: 1px solid rgba(56, 189, 248, 0.18);
        border-radius: 999px;
        padding: 8px 12px;
        font-size: 12px;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #7dd3fc;
        background: rgba(14, 165, 233, 0.08);
      }
      h1 { margin: 18px 0 12px; font-size: 44px; line-height: 1.1; }
      p { margin: 0; color: #94a3b8; }
      .hero {
        display: grid;
        gap: 20px;
        grid-template-columns: 1.2fr 0.8fr;
        margin-top: 28px;
      }
      .tile {
        background: rgba(2, 6, 23, 0.82);
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 24px;
        padding: 20px;
      }
      .metric { font-size: 34px; color: #f8fafc; margin-top: 8px; }
      .summary {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 16px;
        margin-top: 24px;
      }
      .label { color: #7dd3fc; font-size: 13px; text-transform: uppercase; letter-spacing: 0.16em; }
      .checklist { margin-top: 24px; display: grid; gap: 12px; }
      .checklist div {
        padding: 14px 16px;
        border-radius: 18px;
        background: rgba(15, 23, 42, 0.72);
        border: 1px solid rgba(148, 163, 184, 0.12);
      }
    </style>
  </head>
  <body>
    <main class="card">
      <span class="eyebrow">Synthetic release candidate</span>
      <h1 data-testid="checkout-title">Checkout release board</h1>
      <p>Deterministic storefront target used by the TestForge UI suites to validate confirmation, totals, and payment posture.</p>
      <section class="hero">
        <div class="tile">
          <div class="label">Current cart signal</div>
          <div class="metric" data-testid="checkout-summary">SEK 99.00</div>
          <p>3 items, gold shopper persona, VAT-inclusive shipping route.</p>
        </div>
        <div class="tile">
          <div class="label">Payment status</div>
          <div class="metric" data-testid="payment-status">Authorized</div>
          <p>Gateway replay latency within the seeded SLO budget.</p>
        </div>
      </section>
      <div class="summary">
        <section class="tile">
          <strong class="label">Locale</strong>
          <div class="metric">sv-SE</div>
        </section>
        <section class="tile">
          <strong class="label">Release ring</strong>
          <div class="metric">2026.03</div>
        </section>
        <section class="tile">
          <strong class="label">Synthetic env</strong>
          <div class="metric">staging</div>
        </section>
      </div>
      <section class="checklist">
        <div>Receipt total matches API contract snapshot.</div>
        <div>Promo banner discount remains within accepted visual threshold.</div>
        <div>Shipping step stays green on the primary seeded persona.</div>
      </section>
    </main>
  </body>
</html>
"""


@router.get("/target-ui/admin", response_class=HTMLResponse)
async def target_admin_ui() -> str:
    return """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>TestForge Admin Mock</title>
    <style>
      :root { color-scheme: dark; }
      * { box-sizing: border-box; }
      body {
        font-family: "IBM Plex Sans", system-ui, sans-serif;
        background:
          radial-gradient(circle at top right, rgba(45, 212, 191, 0.16), transparent 24%),
          radial-gradient(circle at top left, rgba(56, 189, 248, 0.12), transparent 20%),
          linear-gradient(180deg, #0b1220, #060b14);
        color: #e2e8f0;
        margin: 0;
        min-height: 100vh;
        padding: 40px;
      }
      .card {
        max-width: 1040px;
        margin: 0 auto;
        background: rgba(15, 23, 42, 0.94);
        border: 1px solid rgba(45, 212, 191, 0.16);
        border-radius: 32px;
        padding: 36px;
        box-shadow: 0 28px 80px rgba(2, 6, 23, 0.48);
      }
      .hero {
        display: grid;
        gap: 18px;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        margin-top: 24px;
      }
      .stat, table {
        background: rgba(2, 6, 23, 0.78);
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 24px;
      }
      .stat { padding: 20px; }
      .label { color: #5eead4; font-size: 12px; letter-spacing: 0.18em; text-transform: uppercase; }
      .metric { margin-top: 8px; font-size: 34px; color: #f8fafc; }
      table { width: 100%; border-collapse: collapse; margin-top: 24px; overflow: hidden; }
      td, th { border-bottom: 1px solid #1e293b; padding: 14px 16px; text-align: left; }
      th { color: #94a3b8; font-size: 13px; text-transform: uppercase; letter-spacing: 0.12em; }
      .healthy { color: #6ee7b7; }
      .delayed { color: #fbbf24; }
    </style>
  </head>
  <body>
    <main class="card">
      <h1 data-testid="admin-title">Identity operations board</h1>
      <p>Seeded control-plane target for deterministic RBAC and audit drawer validation.</p>
      <section class="hero">
        <div class="stat">
          <div class="label">Tenants synced</div>
          <div class="metric">4/4</div>
        </div>
        <div class="stat">
          <div class="label">SCIM health</div>
          <div class="metric">Stable</div>
        </div>
        <div class="stat">
          <div class="label">Audit drift</div>
          <div class="metric">Low</div>
        </div>
      </section>
      <table data-testid="roles-table">
        <thead><tr><th>Role</th><th>Sync state</th></tr></thead>
        <tbody>
          <tr><td>admin</td><td class="healthy">healthy</td></tr>
          <tr><td>operator</td><td class="healthy">healthy</td></tr>
          <tr><td>auditor</td><td class="delayed">delayed</td></tr>
        </tbody>
      </table>
    </main>
  </body>
</html>
"""
