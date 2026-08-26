"""LoanVerify — AI-Powered Loan Tape Validator
FastAPI main application.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routes import auth, uploads, validation, audit, exports, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


app = FastAPI(
    title="LoanVerify API",
    description="AI-Powered Loan Data Verification Copilot — Intain FinTech Challenge 2026",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(uploads.router)
app.include_router(validation.router)
app.include_router(audit.router)
app.include_router(exports.router)
app.include_router(chat.router)


@app.get("/")
async def root():
    return {
        "name": "LoanVerify API",
        "version": "1.0.0",
        "description": "AI-Powered Loan Data Verification Copilot",
        "docs": "/docs",
        "challenge": "Intain FinTech Challenge 2026 — Full Stack Track",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
