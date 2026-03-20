from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import UserRole
from app.schemas.common import JsonObject, OrmModel


ThemePreference = Literal["dark", "system"]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserRead(OrmModel):
    id: str
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    title: str = Field(min_length=2, max_length=255)
    role: UserRole
    theme_preference: ThemePreference
    settings: JsonObject
    is_active: bool


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    title: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=6, max_length=128)
    role: UserRole


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    title: str | None = Field(default=None, min_length=2, max_length=255)
    role: UserRole | None = None
    theme_preference: ThemePreference | None = None
    settings: JsonObject | None = None
    is_active: bool | None = None


class ProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    title: str | None = Field(default=None, min_length=2, max_length=255)
    theme_preference: ThemePreference | None = None
    settings: JsonObject | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
