"""
Tenants router — POST /tenants creates a new tenant (organisation).
Required before any user can register, since every user belongs to a tenant.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import uuid
from datetime import datetime

from app.database import get_db
from app.models import Tenant

router = APIRouter(prefix="/tenants", tags=["Tenants"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class TenantCreateRequest(BaseModel):
    name: str
    plan: str = "free"

    class Config:
        json_schema_extra = {
            "example": {"name": "Acme Corp", "plan": "pro"}
        }


class TenantResponse(BaseModel):
    tenant_id: uuid.UUID
    name: str
    plan: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new tenant (organisation)",
)
async def create_tenant(
    payload: TenantCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> TenantResponse:
    if payload.plan not in ("free", "pro", "enterprise"):
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "INVALID_PLAN",
                    "message": "Plan must be one of: free, pro, enterprise.",
                    "field": "plan",
                }
            },
        )

    tenant = Tenant(name=payload.name, plan=payload.plan)
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    return TenantResponse.model_validate(tenant)


@router.get(
    "",
    response_model=list[TenantResponse],
    summary="List all tenants",
)
async def list_tenants(db: AsyncSession = Depends(get_db)) -> list[TenantResponse]:
    result = await db.execute(select(Tenant).order_by(Tenant.created_at.desc()))
    tenants = result.scalars().all()
    return [TenantResponse.model_validate(t) for t in tenants]