"""
Unified Backend API for UtopiaHire Career Services
Combines features from:
- AI Interviewer
- Career Insight Report
- CV Reviewer
- Job Matcher
"""

import logging
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from prometheus_fastapi_instrumentator import Instrumentator



from app.routers import (
    resume,
    interview,
    career_insights,
    job_matching
)
from app.core.rate_limit import limiter

logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}',
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="UtopiaHire Career Services API",
    description=" Unified backend API providing comprehensive career services: ",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

logger.info("Application started successfully")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    resume.router,
    prefix="/api/resume",
    tags=["Resume Analysis"],
    dependencies=[Depends(get_current_user)],
)
app.include_router(
    interview.router,
    prefix="/api/interview",
    tags=["AI Interview"],
    dependencies=[Depends(get_current_user)],
)
app.include_router(
    career_insights.router,
    prefix="/api/career",
    tags=["Career Insights"],
    dependencies=[Depends(get_current_user)],
)
app.include_router(
    job_matching.router,
    prefix="/api/jobs",
    tags=["Job Matching"],
    dependencies=[Depends(get_current_user)],
)

# Add Prometheus metrics instrumentation
Instrumentator().instrument(app).expose(app)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "message": "UtopiaHire Career Services API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
@limiter.limit("5/minute")  # Temporary rate limit for demonstration
async def health_check(request: Request):
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "UtopiaHire Career Services API"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=63072000"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response
