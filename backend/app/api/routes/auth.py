from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.repositories.users import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse, UserRead
from app.schemas.common import ListResponse
from app.services.auth import AuthService


router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    token, user = await AuthService(session).authenticate(payload.email, payload.password)
    await session.commit()
    return TokenResponse(access_token=token, user=UserRead.model_validate(user))


@router.get("/me", response_model=UserRead)
async def me(user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(user)


@router.get("/users", response_model=ListResponse[UserRead])
async def list_users(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> ListResponse[UserRead]:
    users = await UserRepository(session).list_all()
    return ListResponse(items=[UserRead.model_validate(user) for user in users], total=len(users))
