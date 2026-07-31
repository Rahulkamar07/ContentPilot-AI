import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import ContentPilotException, contentpilot_exception_handler
from app.core.logging import logger, setup_logging
from app.core.redis import close_redis_client, init_redis_client


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Graceful application startup and shutdown lifecycle context manager."""
    # Startup sequence
    setup_logging()
    logger.info("Initializing ContentPilot AI Backend Server", environment=settings.ENVIRONMENT)
    await init_redis_client()
    yield
    # Shutdown sequence
    logger.info("Shutting down ContentPilot AI Backend Server")
    await close_redis_client()


def create_application() -> FastAPI:
    """FastAPI Application Factory."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Configure CORS Middleware
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.BACKEND_CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Structlog execution time middleware
    @app.middleware("http")
    async def log_requests_middleware(request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.info(
            "HTTP Request Completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=process_time_ms,
        )
        response.headers["X-Process-Time-Ms"] = str(process_time_ms)
        return response

    # Register Exception Handlers
    app.add_exception_handler(ContentPilotException, contentpilot_exception_handler)

    # Include API Routers
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = create_application()
