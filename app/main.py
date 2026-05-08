"""
DCC User Model — FastAPI application entry point.
Run with:  uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.database import Base, engine
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.tenants import router as tenants_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup (use Alembic migrations in prod)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="DCC User Model",
    description=(
        "User Identity & Authentication Service for a Distributed Cloud Computing platform.\n\n"
        "**Current Part:** Registration + Tenant Management\n\n"
        "**Upcoming:** Login (JWT), Token Refresh, Logout (Redis blacklist), Profile Management"
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tenants_router)


# ── Root ──────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Meta"], summary="Service info")
async def root():
    return {
        "service": "DCC User Model",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }


# ── Health check (standard in cloud deployments) ──────────────────────────────

@app.get("/health", tags=["Meta"], summary="Health check")
async def health():
    from datetime import timezone
    return {
        "status": "healthy",
        "timestamp": __import__("datetime").datetime.now(timezone.utc).isoformat(),
    }


# ── Override FastAPI's default 422 to match the project error envelope ─────────

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    first = exc.errors()[0]
    field = ".".join(str(loc) for loc in first["loc"] if loc != "body")
    msg = first["msg"]

    code = "WEAK_PASSWORD" if "Password" in msg else "VALIDATION_ERROR"

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": code,
                "message": msg,
                "field": field or None,
                "request_id": request.headers.get("X-Request-ID"),
                "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
            }
        },
    )