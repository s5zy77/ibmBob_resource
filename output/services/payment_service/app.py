"""
Payment Processing Microservice - FastAPI Application
Extracted from enterprise_monolith.py using Strangler Fig pattern
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from payment_service.api.routes import router
from payment_service.config import settings
from payment_service import __version__

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("=" * 60)
    logger.info(f"Payment Service v{__version__} starting...")
    logger.info(f"Service URL: http://{settings.SERVICE_HOST}:{settings.SERVICE_PORT}")
    logger.info(f"Payment Gateway: {settings.PAYMENT_GATEWAY_URL}")
    logger.info(f"Max Retries: {settings.MAX_RETRIES}")
    logger.info(f"Currency: {settings.CURRENCY}")
    logger.info(f"Wire Minimum: ${settings.WIRE_MINIMUM}")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("Payment Service shutting down...")


# Create FastAPI application
app = FastAPI(
    title="Payment Processing Service",
    description=(
        "Microservice for payment processing extracted from enterprise monolith. "
        "Supports card, PayPal, and wire transfer payments."
    ),
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "err",
            "message": "Internal server error",
            "detail": str(exc) if settings.LOG_LEVEL == "DEBUG" else None
        }
    )


# Include API routes
app.include_router(router, prefix="/api/v1", tags=["payments"])


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with service information"""
    return {
        "service": "payment-processing-service",
        "version": __version__,
        "status": "running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "api": "/api/v1"
        }
    }


# Additional health check at root level (for load balancers)
@app.get("/health", tags=["health"])
async def health():
    """Health check endpoint (no auth required)"""
    return {
        "status": "healthy",
        "service": "payment-service",
        "version": __version__
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting Payment Service on {settings.SERVICE_HOST}:{settings.SERVICE_PORT}")
    
    uvicorn.run(
        "payment_service.app:app",
        host=settings.SERVICE_HOST,
        port=settings.SERVICE_PORT,
        reload=True,  # Enable auto-reload for development
        log_level=settings.LOG_LEVEL.lower()
    )

# Made with Bob
