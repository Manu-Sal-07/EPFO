import pytest
from fastapi.testclient import TestClient

from pfcompass.api.middleware.rate_limiter import RateLimiterMiddleware
from pfcompass.main import app

client = TestClient(app)


def test_security_headers_present():
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert "strict-origin" in response.headers.get("Referrer-Policy", "")


def test_standardized_error_envelope_404():
    response = client.get("/api/v1/non_existent_route")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert "message" in data["error"]


def test_standardized_error_envelope_422_validation():
    # Invalid data type for email (number instead of string) triggers 422
    response = client.post("/api/v1/auth/login", json={"email": 123, "password": None})
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "details" in data["error"]


def test_rate_limiter_rate_limit_exceeded():
    # Attempt rate limit hit on auth route (limit 10/min)
    path = "/api/v1/auth/login"
    payload = {"email": "rate_limit_test@demo.com", "password": "wrongpassword"}
    
    # First 10 requests should process (401 invalid creds)
    for _ in range(10):
        client.post(path, json=payload)

    # 11th request should trigger HTTP 429
    res_429 = client.post(path, json=payload)
    assert res_429.status_code == 429
    data = res_429.json()
    assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    assert "retry_after_seconds" in data["error"]["details"]
