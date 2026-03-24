from __future__ import annotations

from pydantic import BaseModel, EmailStr

from app.models.enums import UserRole
from app.schemas.common import ORMModel


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserRead(ORMModel):
    id: str
    email: EmailStr
    full_name: str
    role: UserRole


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
