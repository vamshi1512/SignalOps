from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import alerts, audit, auth, config, dashboard, fleet, history, missions, simulator, system


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(fleet.router, prefix="/fleet", tags=["fleet"])
api_router.include_router(missions.router, prefix="/missions", tags=["missions"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(history.router, prefix="/history", tags=["history"])
api_router.include_router(config.router, prefix="/config", tags=["config"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(simulator.router, prefix="/simulator", tags=["simulator"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
