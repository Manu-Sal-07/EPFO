from contextlib import asynccontextmanager
import structlog
from fastapi import Depends, FastAPI, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from pfcompass.database import Base, engine, get_db_session
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from pfcompass import __version__
from pfcompass.api.middleware.rate_limiter import RateLimiterMiddleware
from pfcompass.api.middleware.security_middleware import SecurityHeadersMiddleware
from pfcompass.api.v1 import auth, cases, decision, health, knowledge, system
from pfcompass.config import settings
from pfcompass.seed_demo_data import seed_demo_citizens



logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables and seed demo data on application startup
    logger.info("Initializing database schema and synthetic demo data...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        await seed_demo_citizens()
        logger.info("Database schema and demo data initialized successfully.")
    except Exception as e:
        logger.error("seed_data_failed", error=str(e))
    yield


app = FastAPI(
    title="PF Compass API",
    description="Citizen-first redesign of the EPFO experience",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Middleware Stack (order: Security Headers -> Rate Limiter -> CORS)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Standardized Error Envelopes

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "UNPROCESSABLE_ENTITY",
        429: "RATE_LIMIT_EXCEEDED",
    }
    code = code_map.get(exc.status_code, "HTTP_ERROR")
    return JSONResponse(
        status_code=exc.status_code,
        headers=getattr(exc, "headers", None),
        content={
            "error": {
                "code": code,
                "message": exc.detail if isinstance(exc.detail, str) else "HTTP Request Error",
                "details": exc.detail if not isinstance(exc.detail, str) else None,
            }
        },
    )


@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": {
                "code": "NOT_FOUND",
                "message": f"Endpoint '{request.url.path}' not found.",
                "details": None,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request payload format.",
                "details": exc.errors(),
            }
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("unhandled_exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
                "details": str(exc),
            }
        },
    )


# Include Routers
app.include_router(system.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")
app.include_router(cases.router, prefix="/api/v1")
app.include_router(decision.router, prefix="/api/v1")
app.include_router(knowledge.router, prefix="/api/v1")


@app.get("/")
async def root_redirect() -> dict[str, str]:
    return {
        "message": "PF Compass API Server",
        "docs": "/docs",
        "health": "/api/v1/system/health",
    }


@app.get("/health")
async def direct_health(session: AsyncSession = Depends(get_db_session)):
    return await system.health_check(session=session)


