"""
Main FastAPI application with middleware, routing, and comprehensive configuration.
"""
import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.api.v1.api import api_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting up Generative AI FastAPI Demo")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"API Version: {settings.app_version}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Generative AI FastAPI Demo")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## Generative AI FastAPI Demo

A comprehensive FastAPI demonstration project showcasing modern web API development practices.

### Features

* **User Management**: Complete user registration, authentication, and profile management
* **Item Management**: Full CRUD operations for items with ownership controls
* **JWT Authentication**: Secure token-based authentication system
* **Input Validation**: Comprehensive request/response validation using Pydantic
* **Rate Limiting**: Built-in rate limiting to prevent abuse
* **CORS Support**: Configurable Cross-Origin Resource Sharing
* **Comprehensive Documentation**: Auto-generated OpenAPI/Swagger documentation
* **Error Handling**: Detailed error responses with proper HTTP status codes
* **Logging**: Structured logging for monitoring and debugging

### Authentication

Most endpoints require authentication via Bearer token. To get started:

1. **Register** a new user account using `/api/v1/users/register`
2. **Login** with your credentials using `/api/v1/users/login` to get an access token
3. **Use the token** by adding it to the Authorization header: `Bearer <your-token>`

### API Versioning

This API uses URL versioning with `/api/v1/` prefix for all endpoints.
    """,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
)

# Add trusted host middleware (security)
if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.your-domain.com"]
    )


# Custom middleware for request logging and timing
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing information."""
    start_time = time.time()
    
    # Log request
    logger.info(
        f"Request: {request.method} {request.url} - "
        f"Client: {request.client.host if request.client else 'Unknown'}"
    )
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response
    logger.info(
        f"Response: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    # Add timing header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unexpected errors."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error" if not settings.debug else str(exc),
            "type": "internal_error"
        }
    )


# Health check endpoint
@app.get(
    "/health",
    tags=["health"],
    summary="Health Check",
    description="Check if the API is running and healthy.",
    responses={
        200: {
            "description": "API is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "version": "1.0.0",
                        "timestamp": "2023-01-01T00:00:00"
                    }
                }
            }
        }
    }
)
@limiter.limit(f"{settings.rate_limit_requests * 2}/minute")
async def health_check(request: Request):
    """
    Health check endpoint to verify API status.
    
    Returns basic information about the API health and version.
    """
    from datetime import datetime
    
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat(),
        "app_name": settings.app_name
    }


# Root endpoint
@app.get(
    "/",
    tags=["root"],
    summary="API Root",
    description="Get basic information about the API.",
    responses={
        200: {
            "description": "API information",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Welcome to Generative AI FastAPI Demo",
                        "version": "1.0.0",
                        "docs_url": "/docs",
                        "redoc_url": "/redoc"
                    }
                }
            }
        }
    }
)
@limiter.limit(f"{settings.rate_limit_requests}/minute")
async def root(request: Request):
    """
    Root endpoint providing basic API information.
    
    Returns welcome message and links to documentation.
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "health_check": "/health"
    }


# Include API router
app.include_router(api_router, prefix="/api/v1")


# Custom OpenAPI schema
def custom_openapi():
    """Generate custom OpenAPI schema with additional metadata."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.app_name,
        version=settings.app_version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token in the format: Bearer <token>"
        }
    }
    
    # Add global security requirement
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    # Add custom info
    openapi_schema["info"]["contact"] = {
        "name": "API Support",
        "email": "support@example.com"
    }
    
    openapi_schema["info"]["license"] = {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )