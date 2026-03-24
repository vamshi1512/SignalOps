from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import audit, auth, catalog, dashboard, demo, notifications, runs, system


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(catalog.router, tags=["catalog"])
api_router.include_router(runs.router, tags=["runs"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(notifications.router, tags=["notifications"])
api_router.include_router(demo.router, tags=["demo"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
