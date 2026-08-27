import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pfcompass.config import settings
from pfcompass.models import AuthCredential, Citizen
from pfcompass.schemas.auth import TokenResponse

import bcrypt

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')[:72]
    return bcrypt.hashpw(pwd_bytes, bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode('utf-8')[:72]
    return bcrypt.checkpw(pwd_bytes, hashed_password.encode('utf-8'))


def create_access_token(citizen_id: uuid.UUID) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    payload = {
        "sub": str(citizen_id),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "access",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(citizen_id: uuid.UUID) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(seconds=settings.REFRESH_TOKEN_EXPIRE_SECONDS)
    payload = {
        "sub": str(citizen_id),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "refresh",
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str, expected_type: str = "access") -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        token_type = payload.get("type")
        if token_type != expected_type:
            return None
        sub = payload.get("sub")
        return sub
    except JWTError:
        return None


class AuthService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def authenticate_user(self, email: str, password: str) -> Optional[Citizen]:
        stmt = (
            select(Citizen, AuthCredential)
            .join(AuthCredential, Citizen.id == AuthCredential.citizen_id)
            .where(Citizen.email == email.lower().strip(), Citizen.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        row = result.first()
        if not row:
            return None

        citizen, cred = row
        if not verify_password(password, cred.password_hash):
            cred.failed_attempts += 1
            await self.session.commit()
            return None

        cred.failed_attempts = 0
        cred.last_login_at = datetime.now(timezone.utc)
        await self.session.commit()
        return citizen

    def generate_tokens(self, citizen_id: uuid.UUID) -> TokenResponse:
        access_token = create_access_token(citizen_id)
        refresh_token = create_refresh_token(citizen_id)
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_SECONDS,
            refresh_token=refresh_token
        )
