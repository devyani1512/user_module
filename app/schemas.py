import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator




class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    tenant_id: uuid.UUID
    region: str = "ap-south-1"

    @field_validator("username")
    @classmethod
    def username_length(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters.")
        if len(v) > 100:
            raise ValueError("Username must be at most 100 characters.")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """
        Rules (match the WEAK_PASSWORD error code in the spec):
        - At least 8 characters
        - At least one uppercase letter
        - At least one digit
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit.")
        return v



class RegisterResponse(BaseModel):
    user_id: uuid.UUID
    email: str
    username: str
    tenant_id: uuid.UUID
    region: str
    created_at: datetime




class ErrorDetail(BaseModel):
    code: str
    message: str
    field: str | None = None
    request_id: str | None = None
    timestamp: datetime


class ErrorResponse(BaseModel):
    error: ErrorDetail
