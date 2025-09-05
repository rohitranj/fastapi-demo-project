"""
Item model for database representation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator
from enum import Enum


class ItemStatus(str, Enum):
    """Enum for item status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class Item(BaseModel):
    """
    Item model representing an item in the system.
    """
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    price: float
    status: ItemStatus = ItemStatus.ACTIVE
    owner_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v
    
    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()
    
    model_config = {
        "from_attributes": True,
        "use_enum_values": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "title": "Sample Item",
                "description": "A sample item for demonstration",
                "price": 29.99,
                "status": "active",
                "owner_id": 1,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            }
        }
    }