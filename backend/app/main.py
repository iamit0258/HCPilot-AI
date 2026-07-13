"""FastAPI application entry point for HCPilot AI backend."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base, SessionLocal
from app.models import HCP, Interaction
from app.api import chat, interactions


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Seed database if empty
    db = SessionLocal()
    try:
        if db.query(HCP).count() == 0:
            from seed_data import seed_database
            seed_database()
    except Exception as e:
        print(f"Seed warning: {e}")
    finally:
        db.close()

    yield  # Application runs

    # Shutdown cleanup if needed


app = FastAPI(
    title="HCPilot AI",
    description="AI-First CRM for Intelligent Healthcare Professional Engagement",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware — allow frontend dev server (any localhost/127.0.0.1 port)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_origin_regex="https?://(localhost|127\\.0\\.0\\.1)(:\\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(interactions.router, prefix="/api", tags=["Interactions"])


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "HCPilot AI Backend"}
