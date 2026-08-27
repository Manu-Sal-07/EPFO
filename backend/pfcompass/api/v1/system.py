import redis.asyncio as aioredis
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from pfcompass import __version__
from pfcompass.config import settings
from pfcompass.database import get_db_session
from pfcompass.schemas.system import HealthCheckResponse

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(session: AsyncSession = Depends(get_db_session)) -> HealthCheckResponse:
    # 1. Test database connection
    db_ok = False
    try:
        res = await session.execute(text("SELECT 1"))
        if res.scalar() == 1:
            db_ok = True
    except Exception:
        db_ok = False

    # 2. Test Redis connection
    redis_ok = False
    try:
        r = aioredis.from_url(settings.REDIS_URL, socket_timeout=2.0)
        pong = await r.ping()
        if pong:
            redis_ok = True
        await r.close()
    except Exception:
        redis_ok = False

    status = "healthy" if db_ok else "unhealthy"

    return HealthCheckResponse(
        status=status,
        environment=settings.ENVIRONMENT,
        database=db_ok,
        redis=redis_ok,
        version=__version__
    )
