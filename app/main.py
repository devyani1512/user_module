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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup (for dev — use Alembic migrations in prod)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="DCC User Model — Registration",
    description="User Identity & Authentication Service (Part 1: Registration)",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(auth_router)


# ── Override FastAPI's default 422 to match the project error envelope ────────

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    first = exc.errors()[0]
    field = ".".join(str(loc) for loc in first["loc"] if loc != "body")
    msg = first["msg"]

    # Map pydantic weak-password message to project error code
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
