"""
Basic tests for the FastAPI application using pytest.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.user_service import user_service
from app.schemas.user import UserCreate

client = TestClient(app)


@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "TestPass123",
        "is_active": True,
        "is_superuser": False
    }


@pytest.fixture
def test_item_data():
    """Sample item data for testing."""
    return {
        "title": "Test Item",
        "description": "A test item for unit testing",
        "price": 19.99,
        "status": "active"
    }


@pytest.fixture
async def test_user_token(test_user_data):
    """Create a test user and return authentication token."""
    # Create test user
    user_create = UserCreate(**test_user_data)
    await user_service.create_user(user_create)
    
    # Login to get token
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    response = client.post("/api/v1/users/login", json=login_data)
    assert response.status_code == 200
    
    token_data = response.json()
    return token_data["access_token"]


class TestHealthAndRoot:
    """Test health check and root endpoints."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["docs_url"] == "/docs"
    
    def test_openapi_docs(self):
        """Test that OpenAPI documentation is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
        
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        openapi_data = response.json()
        assert "openapi" in openapi_data
        assert "info" in openapi_data


class TestUserEndpoints:
    """Test user-related endpoints."""
    
    def test_user_registration(self, test_user_data):
        """Test user registration."""
        response = client.post("/api/v1/users/register", json=test_user_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
        assert data["full_name"] == test_user_data["full_name"]
        assert data["is_active"] == test_user_data["is_active"]
        assert "id" in data
        assert "created_at" in data
    
    def test_user_registration_duplicate_email(self, test_user_data):
        """Test user registration with duplicate email."""
        # First registration
        response = client.post("/api/v1/users/register", json=test_user_data)
        assert response.status_code == 201
        
        # Duplicate registration
        duplicate_data = test_user_data.copy()
        duplicate_data["username"] = "differentuser"
        
        response = client.post("/api/v1/users/register", json=duplicate_data)
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]
    
    def test_user_login(self, test_user_data):
        """Test user login."""
        # Register user first
        client.post("/api/v1/users/register", json=test_user_data)
        
        # Login
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/v1/users/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["token_type"] == "bearer"
        assert "access_token" in data
        assert "expires_in" in data
    
    def test_user_login_invalid_credentials(self):
        """Test user login with invalid credentials."""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/users/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_get_current_user(self, test_user_data, test_user_token):
        """Test getting current user information."""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
    
    def test_get_current_user_unauthorized(self):
        """Test getting current user without authentication."""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 403  # FastAPI returns 403 for missing token
    
    @pytest.mark.asyncio
    async def test_update_current_user(self, test_user_data, test_user_token):
        """Test updating current user information."""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        update_data = {"full_name": "Updated Name"}
        
        response = client.put("/api/v1/users/me", json=update_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["full_name"] == "Updated Name"


class TestItemEndpoints:
    """Test item-related endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_item(self, test_item_data, test_user_token):
        """Test item creation."""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.post("/api/v1/items/", json=test_item_data, headers=headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == test_item_data["title"]
        assert data["description"] == test_item_data["description"]
        assert data["price"] == test_item_data["price"]
        assert data["status"] == test_item_data["status"]
        assert "id" in data
        assert "owner_id" in data
    
    def test_create_item_unauthorized(self, test_item_data):
        """Test item creation without authentication."""
        response = client.post("/api/v1/items/", json=test_item_data)
        assert response.status_code == 403
    
    def test_get_items(self):
        """Test getting items list."""
        response = client.get("/api/v1/items/")
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
    
    def test_get_item_by_id(self):
        """Test getting a specific item."""
        # Get items first to find an existing item
        response = client.get("/api/v1/items/")
        assert response.status_code == 200
        
        items_data = response.json()
        if items_data["items"]:
            item_id = items_data["items"][0]["id"]
            
            response = client.get(f"/api/v1/items/{item_id}")
            assert response.status_code == 200
            
            data = response.json()
            assert data["id"] == item_id
    
    def test_get_nonexistent_item(self):
        """Test getting a non-existent item."""
        response = client.get("/api/v1/items/99999")
        assert response.status_code == 404
        assert "Item not found" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_get_my_items(self, test_user_token):
        """Test getting current user's items."""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.get("/api/v1/items/my-items", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data


class TestValidation:
    """Test input validation."""
    
    def test_invalid_user_registration(self):
        """Test user registration with invalid data."""
        invalid_data = {
            "email": "invalid-email",
            "username": "ab",  # Too short
            "password": "123",  # Too weak
        }
        
        response = client.post("/api/v1/users/register", json=invalid_data)
        assert response.status_code == 422
        
        error_detail = response.json()["detail"]
        assert len(error_detail) > 0  # Should have validation errors
    
    @pytest.mark.asyncio
    async def test_invalid_item_creation(self, test_user_token):
        """Test item creation with invalid data."""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        invalid_data = {
            "title": "",  # Empty title
            "price": -10.0,  # Negative price
        }
        
        response = client.post("/api/v1/items/", json=invalid_data, headers=headers)
        assert response.status_code == 422


class TestRateLimit:
    """Test rate limiting functionality."""
    
    def test_rate_limit_health_endpoint(self):
        """Test rate limiting on health endpoint."""
        # Make multiple requests quickly
        responses = []
        for _ in range(5):
            response = client.get("/health")
            responses.append(response.status_code)
        
        # All requests should succeed as we're under the limit
        assert all(status == 200 for status in responses)


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__])