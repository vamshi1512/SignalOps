from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_session
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.auth import LoginRequest, ProfileUpdate, TokenResponse, UserCreate, UserRead, UserUpdate
from app.schemas.common import ListResponse
from app.services.auth import AuthService
from app.services.serializers import serialize_user


router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    token, user = await AuthService(session).authenticate(payload.email, payload.password)
    await session.commit()
    return TokenResponse(access_token=token, user=UserRead.model_validate(user))


@router.get("/me", response_model=UserRead)
async def me(user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(serialize_user(user))


@router.patch("/me", response_model=UserRead)
async def update_me(
    payload: ProfileUpdate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> UserRead:
    updated = await AuthService(session).update_profile(user, payload)
    await session.commit()
    return UserRead.model_validate(serialize_user(updated))


@router.get("/users", response_model=ListResponse[UserRead])
async def list_users(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_roles(UserRole.ADMIN)),
) -> ListResponse[UserRead]:
    users = await AuthService(session).list_users()
    return ListResponse(items=[UserRead.model_validate(serialize_user(user)) for user in users], total=len(users))


@router.post("/users", response_model=UserRead)
async def create_user(
    payload: UserCreate,
    session: AsyncSession = Depends(get_session),
    actor: User = Depends(require_roles(UserRole.ADMIN)),
) -> UserRead:
    user = await AuthService(session).create_user(payload)
    await session.commit()
    return UserRead.model_validate(serialize_user(user))


@router.patch("/users/{user_id}", response_model=UserRead)
async def update_user(
    user_id: str,
    payload: UserUpdate,
    session: AsyncSession = Depends(get_session),
    actor: User = Depends(require_roles(UserRole.ADMIN)),
) -> UserRead:
    _ = actor
    user = await AuthService(session).update_user(user_id, payload)
    await session.commit()
    return UserRead.model_validate(serialize_user(user))
