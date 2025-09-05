"""
API v1 router configuration.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import users, items

api_router = APIRouter()

# Include user endpoints
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

# Include item endpoints
api_router.include_router(
    items.router,
    prefix="/items",
    tags=["items"]
)