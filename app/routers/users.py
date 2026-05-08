"""
Users router — GET /users returns registered users.
Optionally filter by tenant_id for proper multi-tenancy isolation.
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Tenant, User
from app.schemas import UserProfile, UsersListResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "",
    response_model=UsersListResponse,
    summary="List registered users",
    description=(
        "Returns all users. Pass `tenant_id` to scope results to one organisation "
        "(recommended for multi-tenant deployments)."
    ),
)
async def list_users(
    tenant_id: Optional[uuid.UUID] = Query(
        default=None,
        description="Filter users by tenant (organisation) ID",
    ),
    db: AsyncSession = Depends(get_db),
) -> UsersListResponse:

    # If tenant_id provided, verify it exists first
    if tenant_id is not None:
        tenant = await db.get(Tenant, tenant_id)
        if tenant is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "TENANT_NOT_FOUND",
                        "message": f"Tenant {tenant_id} does not exist.",
                    }
                },
            )
        query = select(User).where(User.tenant_id == tenant_id)
    else:
        query = select(User)

    result = await db.execute(query.order_by(User.created_at.desc()))
    users = result.scalars().all()

    return UsersListResponse(
        total=len(users),
        users=[UserProfile.model_validate(u) for u in users],
    )