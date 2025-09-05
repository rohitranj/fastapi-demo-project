"""
Item service layer for business logic and data operations.
"""
from typing import Dict, List, Optional
from datetime import datetime
from fastapi import HTTPException, status
from app.models.item import Item, ItemStatus
from app.schemas.item import ItemCreate, ItemUpdate


class ItemService:
    """Service class for item operations."""
    
    def __init__(self):
        """Initialize the item service with in-memory storage."""
        self._items: Dict[int, Item] = {}
        self._next_id = 1
        
        # Create some sample items
        self._create_sample_items()
    
    def _create_sample_items(self):
        """Create sample items for demonstration."""
        sample_items = [
            ItemCreate(
                title="Premium Headphones",
                description="High-quality wireless headphones with noise cancellation",
                price=199.99,
                status=ItemStatus.ACTIVE
            ),
            ItemCreate(
                title="Smart Watch",
                description="Feature-rich smartwatch with fitness tracking",
                price=299.99,
                status=ItemStatus.ACTIVE
            ),
            ItemCreate(
                title="Bluetooth Speaker",
                description="Portable Bluetooth speaker with excellent sound quality",
                price=79.99,
                status=ItemStatus.INACTIVE
            )
        ]
        
        for item_create in sample_items:
            self._create_item_internal(item_create, owner_id=1)
    
    def _create_item_internal(self, item_create: ItemCreate, owner_id: int) -> Item:
        """Internal method to create an item."""
        item_id = self._next_id
        self._next_id += 1
        
        now = datetime.utcnow()
        
        item = Item(
            id=item_id,
            title=item_create.title,
            description=item_create.description,
            price=item_create.price,
            status=item_create.status,
            owner_id=owner_id,
            created_at=now,
            updated_at=now
        )
        
        self._items[item_id] = item
        return item
    
    async def create_item(self, item_create: ItemCreate, owner_id: int) -> Item:
        """
        Create a new item.
        
        Args:
            item_create: Item creation data
            owner_id: ID of the user creating the item
            
        Returns:
            Created item
        """
        return self._create_item_internal(item_create, owner_id)
    
    async def get_item_by_id(self, item_id: int) -> Optional[Item]:
        """
        Get item by ID.
        
        Args:
            item_id: Item ID
            
        Returns:
            Item if found, None otherwise
        """
        return self._items.get(item_id)
    
    async def get_items(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[ItemStatus] = None,
        owner_id: Optional[int] = None
    ) -> List[Item]:
        """
        Get items with optional filtering and pagination.
        
        Args:
            skip: Number of items to skip
            limit: Maximum number of items to return
            status: Filter by item status
            owner_id: Filter by owner ID
            
        Returns:
            List of items
        """
        items = list(self._items.values())
        
        # Apply filters
        if status:
            items = [item for item in items if item.status == status]
        
        if owner_id:
            items = [item for item in items if item.owner_id == owner_id]
        
        # Sort by creation date (newest first)
        items.sort(key=lambda x: x.created_at, reverse=True)
        
        return items[skip:skip + limit]
    
    async def get_user_items(
        self, 
        owner_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Item]:
        """
        Get items owned by a specific user.
        
        Args:
            owner_id: Owner user ID
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            List of user's items
        """
        return await self.get_items(
            skip=skip, 
            limit=limit, 
            owner_id=owner_id
        )
    
    async def update_item(
        self, 
        item_id: int, 
        item_update: ItemUpdate, 
        user_id: int
    ) -> Optional[Item]:
        """
        Update item information.
        
        Args:
            item_id: Item ID to update
            item_update: Update data
            user_id: ID of the user making the update
            
        Returns:
            Updated item if found and user has permission, None otherwise
            
        Raises:
            HTTPException: If user doesn't have permission to update
        """
        item = self._items.get(item_id)
        if not item:
            return None
        
        # Check if user owns the item or is superuser
        # Note: In a real app, you'd check superuser status from the user object
        if item.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to update this item"
            )
        
        # Update item data
        update_data = item_update.dict(exclude_unset=True)
        if update_data:
            for field, value in update_data.items():
                setattr(item, field, value)
            
            item.updated_at = datetime.utcnow()
        
        return item
    
    async def delete_item(self, item_id: int, user_id: int) -> bool:
        """
        Delete item by ID.
        
        Args:
            item_id: Item ID to delete
            user_id: ID of the user making the deletion
            
        Returns:
            True if item was deleted, False if not found
            
        Raises:
            HTTPException: If user doesn't have permission to delete
        """
        item = self._items.get(item_id)
        if not item:
            return False
        
        # Check if user owns the item or is superuser
        if item.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to delete this item"
            )
        
        del self._items[item_id]
        return True
    
    async def get_item_count(
        self, 
        status: Optional[ItemStatus] = None,
        owner_id: Optional[int] = None
    ) -> int:
        """
        Get total number of items with optional filtering.
        
        Args:
            status: Filter by item status
            owner_id: Filter by owner ID
            
        Returns:
            Total item count
        """
        items = list(self._items.values())
        
        if status:
            items = [item for item in items if item.status == status]
        
        if owner_id:
            items = [item for item in items if item.owner_id == owner_id]
        
        return len(items)


# Global item service instance
item_service = ItemService()