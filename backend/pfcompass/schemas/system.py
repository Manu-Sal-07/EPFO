from typing import Literal
from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    status: Literal["healthy", "degraded", "unhealthy"]
    environment: str
    database: bool
    redis: bool
    version: str
