from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from pfcompass.api.middleware.auth_middleware import get_current_citizen
from pfcompass.database import get_db_session
from pfcompass.models import Citizen
from pfcompass.schemas.auth import (
    CitizenProfileResponse,
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from pfcompass.services.auth_service import AuthService, decode_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db_session)
) -> TokenResponse:
    auth_service = AuthService(session)
    citizen = await auth_service.authenticate_user(payload.email, payload.password)
    if not citizen:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    return auth_service.generate_tokens(citizen.id)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    payload: RefreshTokenRequest,
    session: AsyncSession = Depends(get_db_session)
) -> TokenResponse:
    citizen_id_str = decode_token(payload.refresh_token, expected_type="refresh")
    if not citizen_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    import uuid
    citizen_id = uuid.UUID(citizen_id_str)
    auth_service = AuthService(session)
    return auth_service.generate_tokens(citizen_id)


@router.get("/me", response_model=CitizenProfileResponse)
async def get_my_profile(
    current_citizen: Citizen = Depends(get_current_citizen)
) -> CitizenProfileResponse:
    return CitizenProfileResponse.model_validate(current_citizen)
