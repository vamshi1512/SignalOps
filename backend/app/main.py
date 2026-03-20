from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.router import api_router
from app.core.config import get_settings
from app.core.errors import ApiError, api_error_handler, http_error_handler, validation_error_handler
from app.core.logging import configure_logging, request_id_var
from app.db.session import dispose_engine, get_session_factory, init_db
from app.services.demo import DemoService
from app.simulator.engine import SimulatorCoordinator
from app.ws.manager import WebSocketManager


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    settings = get_settings()
    websocket_manager = WebSocketManager()
    app.state.websocket_manager = websocket_manager
    app.state.simulator = SimulatorCoordinator(get_session_factory(), websocket_manager)

    await init_db()
    if settings.seed_on_start:
        async with get_session_factory()() as session:
            await DemoService(session).seed()
            await session.commit()

    if settings.demo_mode:
        await app.state.simulator.start()

    yield

    await app.state.simulator.stop()
    await dispose_engine()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="RoboYard Control API",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request_id = str(uuid4())
        request.state.request_id = request_id
        token = request_id_var.set(request_id)
        try:
            response = await call_next(request)
        finally:
            request_id_var.reset(token)
        response.headers["X-Request-ID"] = request_id
        return response

    @app.exception_handler(ApiError)
    async def _api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
        return await api_error_handler(request, exc)

    @app.exception_handler(RequestValidationError)
    async def _validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return await validation_error_handler(request, exc)

    @app.exception_handler(HTTPException)
    async def _http_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return await http_error_handler(request, exc)

    app.include_router(api_router, prefix=settings.api_prefix)

    if settings.metrics_enabled:
        Instrumentator().instrument(app).expose(app, include_in_schema=False, endpoint="/metrics")

    return app


app = create_app()
