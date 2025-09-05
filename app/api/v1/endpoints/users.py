"""
User API endpoints with full CRUD operations.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBasicCredentials
from datetime import timedelta
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserLogin, Token
)
from app.models.user import UserInDB
from app.services.user_service import user_service
from app.api.deps import get_current_user, get_current_superuser
from app.core.security import create_access_token, verify_password
from app.core.config import settings

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email, username, and password validation.",
    responses={
        201: {
            "description": "User successfully created",
            "model": UserResponse
        },
        400: {
            "description": "Email already registered or username already taken",
            "content": {
                "application/json": {
                    "example": {"detail": "Email already registered"}
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "password"],
                                "msg": "Password must be at least 8 characters long",
                                "type": "value_error"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def register_user(user_create: UserCreate) -> UserResponse:
    """
    Register a new user.
    
    - **email**: Valid email address (must be unique)
    - **username**: Alphanumeric username, 3+ characters (must be unique)
    - **password**: Strong password with uppercase, lowercase, and digit
    - **full_name**: Optional full name
    - **is_active**: Whether the user is active (default: true)
    - **is_superuser**: Whether the user has admin privileges (default: false)
    """
    user = await user_service.create_user(user_create)
    return UserResponse(**user.dict())


@router.post(
    "/login",
    response_model=Token,
    summary="User login",
    description="Authenticate user and return JWT access token.",
    responses={
        200: {
            "description": "Login successful",
            "model": Token
        },
        401: {
            "description": "Invalid credentials or inactive user",
            "content": {
                "application/json": {
                    "example": {"detail": "Incorrect username or password"}
                }
            }
        }
    }
)
async def login(user_login: UserLogin) -> Token:
    """
    Login user and get access token.
    
    - **username**: Username for authentication
    - **password**: User password
    
    Returns JWT token with expiration information.
    """
    user = await user_service.authenticate_user(
        user_login.username, user_login.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get the current authenticated user's information.",
    responses={
        200: {
            "description": "Current user information",
            "model": UserResponse
        },
        401: {
            "description": "Not authenticated",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            }
        }
    }
)
async def get_current_user_info(
    current_user: UserInDB = Depends(get_current_user)
) -> UserResponse:
    """
    Get current user information.
    
    Requires authentication via Bearer token.
    """
    return UserResponse(**current_user.dict())


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user",
    description="Update the current authenticated user's information.",
    responses={
        200: {
            "description": "User successfully updated",
            "model": UserResponse
        },
        400: {
            "description": "Email already registered or username already taken"
        },
        401: {
            "description": "Not authenticated"
        }
    }
)
async def update_current_user(
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_user)
) -> UserResponse:
    """
    Update current user information.
    
    - **email**: New email address (must be unique if provided)
    - **username**: New username (must be unique if provided)
    - **full_name**: New full name
    - **is_active**: Update active status
    
    Requires authentication via Bearer token.
    """
    user = await user_service.update_user(current_user.id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse(**user.dict())


@router.get(
    "/",
    response_model=List[UserResponse],
    summary="Get all users",
    description="Get a list of all users (admin only).",
    dependencies=[Depends(get_current_superuser)],
    responses={
        200: {
            "description": "List of users",
            "model": List[UserResponse]
        },
        403: {
            "description": "Not enough permissions"
        }
    }
)
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of users to return")
) -> List[UserResponse]:
    """
    Get all users with pagination (admin only).
    
    - **skip**: Number of users to skip (default: 0)
    - **limit**: Maximum number of users to return (default: 100, max: 1000)
    
    Requires superuser privileges.
    """
    users = await user_service.get_all_users(skip=skip, limit=limit)
    return [UserResponse(**user.dict()) for user in users]


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Get a specific user by their ID (admin only).",
    dependencies=[Depends(get_current_superuser)],
    responses={
        200: {
            "description": "User information",
            "model": UserResponse
        },
        403: {
            "description": "Not enough permissions"
        },
        404: {
            "description": "User not found"
        }
    }
)
async def get_user(user_id: int) -> UserResponse:
    """
    Get user by ID (admin only).
    
    - **user_id**: The ID of the user to retrieve
    
    Requires superuser privileges.
    """
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse(**user.dict())


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user by ID",
    description="Update a specific user by their ID (admin only).",
    dependencies=[Depends(get_current_superuser)],
    responses={
        200: {
            "description": "User successfully updated",
            "model": UserResponse
        },
        400: {
            "description": "Email already registered or username already taken"
        },
        403: {
            "description": "Not enough permissions"
        },
        404: {
            "description": "User not found"
        }
    }
)
async def update_user(user_id: int, user_update: UserUpdate) -> UserResponse:
    """
    Update user by ID (admin only).
    
    - **user_id**: The ID of the user to update
    - **email**: New email address (must be unique if provided)
    - **username**: New username (must be unique if provided)
    - **full_name**: New full name
    - **is_active**: Update active status
    - **is_superuser**: Update superuser status
    
    Requires superuser privileges.
    """
    user = await user_service.update_user(user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse(**user.dict())


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user by ID",
    description="Delete a specific user by their ID (admin only).",
    dependencies=[Depends(get_current_superuser)],
    responses={
        204: {
            "description": "User successfully deleted"
        },
        403: {
            "description": "Not enough permissions"
        },
        404: {
            "description": "User not found"
        }
    }
)
async def delete_user(user_id: int):
    """
    Delete user by ID (admin only).
    
    - **user_id**: The ID of the user to delete
    
    Requires superuser privileges.
    """
    deleted = await user_service.delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )