import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

import database
import models
import scheduler
from notifications import notification_manager
from routers import auth as auth_router
from routers import hosts as hosts_router
from routers import status as status_router
from routers import tools as tools_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager replacing deprecated FastAPI on_event handlers."""
    logger.info("Initializing database migrations & models...")
    database.migrate_db()
    models.Base.metadata.create_all(bind=database.engine)

    logger.info("Starting background scheduler...")
    scheduler.start_scheduler()

    db = database.SessionLocal()
    try:
        notification_manager.load_config(db)
    finally:
        db.close()

    yield

    logger.info("Shutting down background scheduler...")
    if scheduler.scheduler.running:
        scheduler.scheduler.shutdown(wait=False)


app = FastAPI(
    title="Network Monitor API",
    version="1.0.0",
    lifespan=lifespan,
)

# Slowapi rate limiter setup
app.state.limiter = auth_router.limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware with environment-based origins support
cors_origins_env = os.getenv("CORS_ORIGINS", "*")
origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


app.add_middleware(SecurityHeadersMiddleware)

# Include Routers
app.include_router(auth_router.router)
app.include_router(hosts_router.router)
app.include_router(status_router.router)
app.include_router(tools_router.router)

# Backward-compatibility exports for test suite
_audit = tools_router._audit
ping = tools_router.ping
