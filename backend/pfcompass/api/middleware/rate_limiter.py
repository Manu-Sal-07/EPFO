"""
Rate Limiter Middleware for FastAPI.

Implements an in-memory sliding window rate limiter per client IP.
Protects sensitive routes against brute-force attacks and resource exhaustion.
"""

import time
from collections import defaultdict
from typing import Dict, List, Tuple
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Sliding window rate limiter middleware.
    Route limits:
    - /api/v1/auth/login: 10 requests / minute
    - /api/v1/*/explain: 20 requests / minute
    - Default: 120 requests / minute
    """

    def __init__(self, app):
        super().__init__(app)
        # ip -> list of timestamps
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def _get_limit_for_path(self, path: str) -> Tuple[int, int]:
        """Returns (max_requests, window_seconds)."""
        if "/auth/login" in path:
            return 10, 60
        if "/explain" in path:
            return 20, 60
        return 120, 60

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip health check endpoints
        if request.url.path in ("/api/v1/system/health", "/docs", "/openapi.json", "/redoc", "/"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "127.0.0.1"
        key = f"{client_ip}:{request.url.path}"
        
        max_requests, window_seconds = self._get_limit_for_path(request.url.path)
        now = time.time()
        window_start = now - window_seconds

        # Clean old timestamps
        self.requests[key] = [ts for ts in self.requests[key] if ts > window_start]

        if len(self.requests[key]) >= max_requests:
            retry_after = int(window_seconds - (now - self.requests[key][0])) + 1
            return JSONResponse(
                status_code=429,
                headers={"Retry-After": str(retry_after)},
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": f"Rate limit exceeded. Maximum {max_requests} requests allowed per minute on this endpoint.",
                        "details": {"retry_after_seconds": retry_after}
                    }
                }
            )

        self.requests[key].append(now)
        return await call_next(request)
