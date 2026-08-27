import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from pfcompass.database import get_db_session
from pfcompass.models import Citizen
from pfcompass.repositories.citizen_repo import CitizenRepository
from pfcompass.services.auth_service import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_citizen(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db_session)
) -> Citizen:
    citizen_id_str = decode_token(token, expected_type="access")
    if not citizen_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        citizen_id = uuid.UUID(citizen_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token subject",
            headers={"WWW-Authenticate": "Bearer"}
        )

    repo = CitizenRepository(session)
    citizen = await repo.get_by_id(citizen_id)
    if not citizen:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Citizen not found or deactivated",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return citizen
