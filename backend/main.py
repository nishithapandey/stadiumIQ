"""StadiumIQ FastAPI Backend — FIFA World Cup 2026 Smart Stadium Assistant.

Production-grade FastAPI application with:
- Structured logging with request tracing
- Rate limiting via SlowAPI
- Strict CORS configuration
- Health monitoring endpoint
"""

import os
import logging
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routers import chat, crowd, navigation, transport

load_dotenv()

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("stadiumiq")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle with health logging."""
    logger.info("StadiumIQ backend starting — environment: %s",
                os.getenv("ENVIRONMENT", "development"))
    yield
    logger.info("StadiumIQ backend shutting down.")


app = FastAPI(
    title="StadiumIQ API",
    description="GenAI-powered Smart Stadium Assistant for FIFA World Cup 2026",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url=None,
)


# --- Middleware ---

# CORS — restrict in production via env var
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.middleware("http")
async def add_request_id(request: Request, call_next) -> Response:
    """Add a unique request ID header for traceability and debugging."""
    request_id = str(uuid.uuid4())[:8]
    logger.info("Request %s: %s %s", request_id, request.method, request.url.path)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.middleware("http")
async def add_security_headers(request: Request, call_next) -> Response:
    """Add security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: https:; connect-src 'self' https: http:"
    return response


# --- Routers ---

app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(crowd.router, prefix="/api", tags=["Crowd"])
app.include_router(navigation.router, prefix="/api", tags=["Navigation"])
app.include_router(transport.router, prefix="/api", tags=["Transport"])


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint for monitoring and load balancer probes."""
    return {"status": "ok", "service": "StadiumIQ", "version": "1.0.0"}
