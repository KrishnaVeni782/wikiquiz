"""
app/main.py
────────────
FastAPI application factory.

Run locally:
    cd backend
    uvicorn app.main:app --reload --port 8000
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import engine, Base
from app.api.routes import router

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s – %(message)s",
)

# ── Create tables on startup ──────────────────────────────────────────────────
# In production you would use Alembic migrations instead.
Base.metadata.create_all(bind=engine)

# ── App factory ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="WikiQuiz API",
    description=(
        "Accepts a Wikipedia article URL, scrapes the content, "
        "generates a quiz using an LLM, and persists everything in PostgreSQL."
    ),
    version="1.0.0",
    docs_url="/docs",          # Swagger UI
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(router, prefix="/api")

# ── Root redirect to docs ─────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
def root():
    return {"message": "WikiQuiz API — visit /docs for the interactive API explorer."}
