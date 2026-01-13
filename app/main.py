from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import health, goals, roadmap_assistant, note_assistant, analysis

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(goals.router, prefix=settings.api_prefix, tags=["Goals"])
app.include_router(roadmap_assistant.router, prefix=settings.api_prefix, tags=["Roadmap Assistant"])
app.include_router(note_assistant.router, prefix=settings.api_prefix, tags=["Note Assistant"])
app.include_router(analysis.router, prefix=settings.api_prefix, tags=["Analysis"])

@app.get("/")
async def root():
    return {
        "message": "AI Tutor API",
        "version": settings.api_version,
        "docs": "/docs"
    }