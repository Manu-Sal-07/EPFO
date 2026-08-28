import os
import structlog
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from pfcompass.config import settings

logger = structlog.get_logger()

db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

is_vercel = "VERCEL" in os.environ
use_local_sqlite = os.environ.get("USE_LOCAL_SQLITE")

if use_local_sqlite is not None:
    should_use_sqlite = use_local_sqlite.lower() == "true"
elif is_vercel:
    should_use_sqlite = "sqlite" in db_url
else:
    should_use_sqlite = "sqlite" in db_url or settings.ENVIRONMENT == "development"

if should_use_sqlite:
    sqlite_file = "/tmp/pfcompass.db" if is_vercel else "./pfcompass.db"
    db_url = f"sqlite+aiosqlite:///{sqlite_file}"
    engine = create_async_engine(
        db_url,
        echo=(settings.LOG_LEVEL.upper() == "DEBUG"),
        future=True,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_async_engine(
        db_url,
        echo=(settings.LOG_LEVEL.upper() == "DEBUG"),
        future=True,
        pool_pre_ping=True
    )

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


class Base(DeclarativeBase):
    pass


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
