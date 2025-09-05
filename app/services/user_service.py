"""
User service layer for business logic and data operations.
"""
from typing import Dict, List, Optional
from datetime import datetime
from fastapi import HTTPException, status
from app.models.user import User, UserInDB
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class UserService:
    """Service class for user operations."""
    
    def __init__(self):
        """Initialize the user service with in-memory storage."""
        self._users: Dict[int, UserInDB] = {}
        self._user_by_email: Dict[str, int] = {}
        self._user_by_username: Dict[str, int] = {}
        self._next_id = 1
        
        # Create a default admin user
        admin_user = UserCreate(
            email="admin@example.com",
            username="admin",
            full_name="System Administrator",
            password="AdminPass123",
            is_active=True,
            is_superuser=True
        )
        self._create_user_sync(admin_user)
    
    def _create_user_sync(self, user_create: UserCreate) -> UserInDB:
        """
        Synchronous user creation for initialization.
        
        Args:
            user_create: User creation data
            
        Returns:
            Created user
        """
        # Create new user
        user_id = self._next_id
        self._next_id += 1
        
        hashed_password = get_password_hash(user_create.password)
        now = datetime.utcnow()
        
        user = UserInDB(
            id=user_id,
            email=user_create.email,
            username=user_create.username,
            full_name=user_create.full_name,
            hashed_password=hashed_password,
            is_active=user_create.is_active,
            is_superuser=user_create.is_superuser,
            created_at=now,
            updated_at=now
        )
        
        self._users[user_id] = user
        self._user_by_email[user_create.email] = user_id
        self._user_by_username[user_create.username] = user_id
        
        return user
    
    async def create_user(self, user_create: UserCreate) -> UserInDB:
        """
        Create a new user.
        
        Args:
            user_create: User creation data
            
        Returns:
            Created user
            
        Raises:
            HTTPException: If email or username already exists
        """
        # Check if email already exists
        if user_create.email in self._user_by_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username already exists
        if user_create.username in self._user_by_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create new user
        user_id = self._next_id
        self._next_id += 1
        
        hashed_password = get_password_hash(user_create.password)
        now = datetime.utcnow()
        
        user = UserInDB(
            id=user_id,
            email=user_create.email,
            username=user_create.username,
            full_name=user_create.full_name,
            hashed_password=hashed_password,
            is_active=user_create.is_active,
            is_superuser=user_create.is_superuser,
            created_at=now,
            updated_at=now
        )
        
        self._users[user_id] = user
        self._user_by_email[user_create.email] = user_id
        self._user_by_username[user_create.username] = user_id
        
        return user
    
    async def get_user_by_id(self, user_id: int) -> Optional[UserInDB]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User if found, None otherwise
        """
        return self._users.get(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """
        Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User if found, None otherwise
        """
        user_id = self._user_by_email.get(email)
        if user_id:
            return self._users.get(user_id)
        return None
    
    async def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        """
        Get user by username.
        
        Args:
            username: Username
            
        Returns:
            User if found, None otherwise
        """
        user_id = self._user_by_username.get(username)
        if user_id:
            return self._users.get(user_id)
        return None
    
    async def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        """
        Authenticate user with username/password.
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            User if authentication successful, None otherwise
        """
        user = await self.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user
    
    async def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[UserInDB]:
        """
        Update user information.
        
        Args:
            user_id: User ID to update
            user_update: Update data
            
        Returns:
            Updated user if found, None otherwise
            
        Raises:
            HTTPException: If email or username conflicts exist
        """
        user = self._users.get(user_id)
        if not user:
            return None
        
        # Check for email conflicts
        if user_update.email and user_update.email != user.email:
            if user_update.email in self._user_by_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Check for username conflicts
        if user_update.username and user_update.username != user.username:
            if user_update.username in self._user_by_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Update user data
        update_data = user_update.dict(exclude_unset=True)
        if update_data:
            # Remove old email/username mappings if they're being changed
            if user_update.email and user_update.email != user.email:
                del self._user_by_email[user.email]
                self._user_by_email[user_update.email] = user_id
            
            if user_update.username and user_update.username != user.username:
                del self._user_by_username[user.username]
                self._user_by_username[user_update.username] = user_id
            
            # Update user object
            for field, value in update_data.items():
                setattr(user, field, value)
            
            user.updated_at = datetime.utcnow()
        
        return user
    
    async def delete_user(self, user_id: int) -> bool:
        """
        Delete user by ID.
        
        Args:
            user_id: User ID to delete
            
        Returns:
            True if user was deleted, False if not found
        """
        user = self._users.get(user_id)
        if not user:
            return False
        
        # Remove from all mappings
        del self._users[user_id]
        del self._user_by_email[user.email]
        del self._user_by_username[user.username]
        
        return True
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserInDB]:
        """
        Get all users with pagination.
        
        Args:
            skip: Number of users to skip
            limit: Maximum number of users to return
            
        Returns:
            List of users
        """
        users = list(self._users.values())
        return users[skip:skip + limit]
    
    async def get_user_count(self) -> int:
        """
        Get total number of users.
        
        Returns:
            Total user count
        """
        return len(self._users)


# Global user service instance
user_service = UserService()