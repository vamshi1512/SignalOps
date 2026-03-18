from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import alerts, audit, auth, dashboard, demo, incidents, logs, services, system


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(demo.router, prefix="/demo", tags=["demo"])
api_router.include_router(system.router, prefix="/system", tags=["system"])

