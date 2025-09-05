"""
Item schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator
from app.models.item import ItemStatus


class ItemBase(BaseModel):
    """Base item schema with common fields."""
    title: str
    description: Optional[str] = None
    price: float
    status: ItemStatus = ItemStatus.ACTIVE
    
    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return round(v, 2)
    
    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()


class ItemCreate(ItemBase):
    """Schema for item creation requests."""
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Sample Product",
                "description": "A high-quality sample product for demonstration",
                "price": 29.99,
                "status": "active"
            }
        }
    }


class ItemUpdate(BaseModel):
    """Schema for item update requests."""
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    status: Optional[ItemStatus] = None
    
    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Price must be greater than 0")
        return round(v, 2) if v is not None else v
    
    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Title cannot be empty")
            return v.strip()
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Updated Product Title",
                "description": "Updated product description",
                "price": 39.99,
                "status": "active"
            }
        }
    }


class ItemResponse(ItemBase):
    """Schema for item response data."""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "title": "Sample Product",
                "description": "A high-quality sample product for demonstration",
                "price": 29.99,
                "status": "active",
                "owner_id": 1,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            }
        }
    }


class ItemList(BaseModel):
    """Schema for paginated item list response."""
    items: list[ItemResponse]
    total: int
    page: int
    size: int
    pages: int
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "items": [
                    {
                        "id": 1,
                        "title": "Sample Product",
                        "description": "A high-quality sample product",
                        "price": 29.99,
                        "status": "active",
                        "owner_id": 1,
                        "created_at": "2023-01-01T00:00:00",
                        "updated_at": "2023-01-01T00:00:00"
                    }
                ],
                "total": 1,
                "page": 1,
                "size": 10,
                "pages": 1
            }
        }
    }