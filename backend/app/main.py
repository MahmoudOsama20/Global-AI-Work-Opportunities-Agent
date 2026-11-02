from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.config import settings
from app.api.routes import opportunities, sources, pipeline, discovery, profile, reports, cv
from app.database.session import init_db

app = FastAPI(
    title="Global AI Opportunities Intelligence Agent",
    description="Backend API service for global AI work discovery, intelligence matching, and reports.",
    version="0.1.0",
)

# Enable CORS for local Vite development frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API subrouters
app.include_router(opportunities.router, prefix="/api")
app.include_router(sources.router, prefix="/api")
app.include_router(pipeline.router, prefix="/api")
app.include_router(discovery.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(cv.router, prefix="/api")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/api/health")
def health_endpoint():
    return {"status": "ok", "service": "Global AI Opportunities Agent"}

# Mount built frontend SPA if available (after API routes)
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="static")
