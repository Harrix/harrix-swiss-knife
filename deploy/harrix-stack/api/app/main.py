"""Minimal FastAPI stub for harrix.dev (`/api`) with per-IP rate limiting."""

import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address


def client_ip(request: Request) -> str:
    """Return the visitor IP set by Caddy (`X-Real-IP`); the API is reachable only via Caddy."""
    return request.headers.get("x-real-ip") or get_remote_address(request)


async def health(request: Request) -> dict[str, str]:  # noqa: ARG001
    """Liveness probe."""
    return {"status": "ok"}


async def search(request: Request, q: str = "") -> dict[str, object]:  # noqa: ARG001
    """Search stub; the real index is wired later."""
    return {"query": q.strip()[:200], "results": []}


RATE_LIMIT = os.environ.get("API_RATE_LIMIT", "30/minute")
CORS_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("CORS_ORIGINS", "https://harrix.dev,https://www.harrix.dev").split(",")
    if origin.strip()
]

limiter = Limiter(key_func=client_ip)
app = FastAPI(title="harrix.dev API", version="0.1.0", docs_url=None, redoc_url=None, openapi_url=None)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
app.add_api_route("/api/health", limiter.limit(RATE_LIMIT)(health), methods=["GET"])
app.add_api_route("/api/search", limiter.limit(RATE_LIMIT)(search), methods=["GET"])
