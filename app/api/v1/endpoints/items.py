"""
Item API endpoints with full CRUD operations.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.item import (
    ItemCreate, ItemUpdate, ItemResponse, ItemList
)
from app.models.user import UserInDB
from app.models.item import ItemStatus
from app.services.item_service import item_service
from app.api.deps import get_current_user, get_optional_current_user
import math

router = APIRouter()


@router.post(
    "/",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new item",
    description="Create a new item. Requires authentication.",
    responses={
        201: {
            "description": "Item successfully created",
            "model": ItemResponse
        },
        401: {
            "description": "Not authenticated"
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "price"],
                                "msg": "Price must be greater than 0",
                                "type": "value_error"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def create_item(
    item_create: ItemCreate,
    current_user: UserInDB = Depends(get_current_user)
) -> ItemResponse:
    """
    Create a new item.
    
    - **title**: Item title (required, non-empty)
    - **description**: Item description (optional)
    - **price**: Item price (required, must be greater than 0)
    - **status**: Item status (active, inactive, archived - default: active)
    
    Requires authentication via Bearer token.
    """
    item = await item_service.create_item(item_create, current_user.id)
    return ItemResponse(**item.dict())


@router.get(
    "/",
    response_model=ItemList,
    summary="Get all items",
    description="Get a paginated list of items with optional filtering.",
    responses={
        200: {
            "description": "List of items with pagination info",
            "model": ItemList
        }
    }
)
async def get_items(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[ItemStatus] = Query(None, description="Filter by item status"),
    current_user: Optional[UserInDB] = Depends(get_optional_current_user())
) -> ItemList:
    """
    Get all items with pagination and filtering.
    
    - **page**: Page number starting from 1
    - **size**: Number of items per page (max 100)
    - **status**: Optional filter by item status (active, inactive, archived)
    
    Authentication is optional. Returns public items or user's items if authenticated.
    """
    skip = (page - 1) * size
    
    items = await item_service.get_items(
        skip=skip,
        limit=size,
        status=status
    )
    
    total = await item_service.get_item_count(status=status)
    pages = math.ceil(total / size) if total > 0 else 1
    
    item_responses = [ItemResponse(**item.dict()) for item in items]
    
    return ItemList(
        items=item_responses,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get(
    "/my-items",
    response_model=ItemList,
    summary="Get current user's items",
    description="Get a paginated list of items owned by the current user.",
    responses={
        200: {
            "description": "List of user's items with pagination info",
            "model": ItemList
        },
        401: {
            "description": "Not authenticated"
        }
    }
)
async def get_my_items(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: UserInDB = Depends(get_current_user)
) -> ItemList:
    """
    Get current user's items with pagination.
    
    - **page**: Page number starting from 1
    - **size**: Number of items per page (max 100)
    
    Requires authentication via Bearer token.
    """
    skip = (page - 1) * size
    
    items = await item_service.get_user_items(
        owner_id=current_user.id,
        skip=skip,
        limit=size
    )
    
    total = await item_service.get_item_count(owner_id=current_user.id)
    pages = math.ceil(total / size) if total > 0 else 1
    
    item_responses = [ItemResponse(**item.dict()) for item in items]
    
    return ItemList(
        items=item_responses,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Get item by ID",
    description="Get a specific item by its ID.",
    responses={
        200: {
            "description": "Item information",
            "model": ItemResponse
        },
        404: {
            "description": "Item not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Item not found"}
                }
            }
        }
    }
)
async def get_item(item_id: int) -> ItemResponse:
    """
    Get item by ID.
    
    - **item_id**: The ID of the item to retrieve
    
    No authentication required for public item access.
    """
    item = await item_service.get_item_by_id(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    return ItemResponse(**item.dict())


@router.put(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Update item by ID",
    description="Update a specific item by its ID. Only the item owner can update it.",
    responses={
        200: {
            "description": "Item successfully updated",
            "model": ItemResponse
        },
        401: {
            "description": "Not authenticated"
        },
        403: {
            "description": "Not enough permissions (not the item owner)"
        },
        404: {
            "description": "Item not found"
        },
        422: {
            "description": "Validation error"
        }
    }
)
async def update_item(
    item_id: int,
    item_update: ItemUpdate,
    current_user: UserInDB = Depends(get_current_user)
) -> ItemResponse:
    """
    Update item by ID.
    
    - **item_id**: The ID of the item to update
    - **title**: New item title
    - **description**: New item description
    - **price**: New item price (must be greater than 0)
    - **status**: New item status
    
    Only the item owner can update the item.
    Requires authentication via Bearer token.
    """
    item = await item_service.update_item(item_id, item_update, current_user.id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    return ItemResponse(**item.dict())


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete item by ID",
    description="Delete a specific item by its ID. Only the item owner can delete it.",
    responses={
        204: {
            "description": "Item successfully deleted"
        },
        401: {
            "description": "Not authenticated"
        },
        403: {
            "description": "Not enough permissions (not the item owner)"
        },
        404: {
            "description": "Item not found"
        }
    }
)
async def delete_item(
    item_id: int,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Delete item by ID.
    
    - **item_id**: The ID of the item to delete
    
    Only the item owner can delete the item.
    Requires authentication via Bearer token.
    """
    deleted = await item_service.delete_item(item_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )


@router.patch(
    "/{item_id}/status",
    response_model=ItemResponse,
    summary="Update item status",
    description="Update only the status of a specific item.",
    responses={
        200: {
            "description": "Item status successfully updated",
            "model": ItemResponse
        },
        401: {
            "description": "Not authenticated"
        },
        403: {
            "description": "Not enough permissions (not the item owner)"
        },
        404: {
            "description": "Item not found"
        }
    }
)
async def update_item_status(
    item_id: int,
    status: ItemStatus,
    current_user: UserInDB = Depends(get_current_user)
) -> ItemResponse:
    """
    Update item status only.
    
    - **item_id**: The ID of the item to update
    - **status**: New item status (active, inactive, archived)
    
    Convenience endpoint for updating only the item status.
    Only the item owner can update the item.
    Requires authentication via Bearer token.
    """
    item_update = ItemUpdate(status=status)
    item = await item_service.update_item(item_id, item_update, current_user.id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    return ItemResponse(**item.dict())