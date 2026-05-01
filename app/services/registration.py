"""
Registration service — contains all business logic for user creation.
Kept separate from the route so it can be unit-tested without HTTP overhead.
"""

import uuid
from datetime import datetime, timezone

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Tenant, User
from app.schemas import RegisterRequest, RegisterResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


# ── Custom exceptions (mapped to HTTP codes in the router) ────────────────────

class EmailAlreadyExists(Exception):
    pass


class UsernameTaken(Exception):
    pass


class TenantNotFound(Exception):
    pass


# ── Core function ─────────────────────────────────────────────────────────────

async def register_user(
    db: AsyncSession,
    payload: RegisterRequest,
) -> RegisterResponse:
    """
    1. Verify tenant exists.
    2. Check email uniqueness.
    3. Check username uniqueness within tenant.
    4. Hash password (bcrypt, cost 12).
    5. Insert user row.
    6. Return RegisterResponse — no token issued at registration.
    """

    # 1 — Tenant must exist
    tenant = await db.get(Tenant, payload.tenant_id)
    if tenant is None:
        raise TenantNotFound(f"Tenant {payload.tenant_id} does not exist.")

    # 2 — Email uniqueness (global)
    existing_email = await db.scalar(
        select(User).where(User.email == payload.email.lower())
    )
    if existing_email:
        raise EmailAlreadyExists(f"Email '{payload.email}' is already registered.")

    # 3 — Username uniqueness within tenant
    existing_username = await db.scalar(
        select(User).where(
            User.username == payload.username,
            User.tenant_id == payload.tenant_id,
        )
    )
    if existing_username:
        raise UsernameTaken(f"Username '{payload.username}' is already taken.")

    # 4 — Hash password
    password_hash = pwd_context.hash(payload.password)

    # 5 — Create user
    new_user = User(
        email=payload.email.lower(),
        username=payload.username,
        password_hash=password_hash,
        tenant_id=payload.tenant_id,
        region=payload.region,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # 6 — Build response (no token — spec says "201 Created with user_id and email")
    return RegisterResponse(
        user_id=new_user.user_id,
        email=new_user.email,
        username=new_user.username,
        tenant_id=new_user.tenant_id,
        region=new_user.region,
        created_at=new_user.created_at,
    )
