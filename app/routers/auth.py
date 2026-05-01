"""
Auth router — currently exposes only POST /auth/register.
Login, logout, and refresh will be added in later parts.
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import ErrorDetail, ErrorResponse, RegisterRequest, RegisterResponse
from app.services.registration import (
    EmailAlreadyExists,
    TenantNotFound,
    UsernameTaken,
    register_user,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _error(
    status_code: int,
    code: str,
    message: str,
    request_id: str | None = None,
    field: str | None = None,
) -> HTTPException:
    """Build a consistent error HTTPException matching the spec envelope."""
    body = ErrorResponse(
        error=ErrorDetail(
            code=code,
            message=message,
            field=field,
            request_id=request_id,
            timestamp=datetime.now(timezone.utc),
        )
    )
    return HTTPException(status_code=status_code, detail=body.model_dump(mode="json"))


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    responses={
        409: {"model": ErrorResponse, "description": "Email or username conflict"},
        422: {"model": ErrorResponse, "description": "Weak password or bad input"},
    },
)
async def register(
    payload: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> RegisterResponse:
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    try:
        return await register_user(db, payload)

    except TenantNotFound as exc:
        raise _error(404, "TENANT_NOT_FOUND", str(exc), request_id) from exc

    except EmailAlreadyExists as exc:
        raise _error(409, "EMAIL_ALREADY_EXISTS", str(exc), request_id, field="email") from exc

    except UsernameTaken as exc:
        raise _error(409, "USERNAME_TAKEN", str(exc), request_id, field="username") from exc
