"""StadiumIQ FastAPI Backend — FIFA World Cup 2026 Smart Stadium Assistant"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routers import chat, crowd, navigation, transport

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    print("StadiumIQ backend starting…")
    yield
    print("StadiumIQ backend shutting down.")


app = FastAPI(
    title="StadiumIQ API",
    description="GenAI-powered Smart Stadium Assistant for FIFA World Cup 2026",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — restrict in production via env var
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(crowd.router, prefix="/api", tags=["Crowd"])
app.include_router(navigation.router, prefix="/api", tags=["Navigation"])
app.include_router(transport.router, prefix="/api", tags=["Transport"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "StadiumIQ"}
