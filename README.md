# Generative AI FastAPI Demo

A comprehensive, production-ready FastAPI demonstration project showcasing modern web API development best practices, complete with authentication, CRUD operations, comprehensive documentation, and testing.

## 🚀 Features

- **User Management**: Complete user registration, authentication, and profile management
- **Item Management**: Full CRUD operations for items with ownership controls
- **JWT Authentication**: Secure token-based authentication system with Bearer tokens
- **Input Validation**: Comprehensive request/response validation using Pydantic models
- **Rate Limiting**: Built-in rate limiting to prevent API abuse
- **CORS Support**: Configurable Cross-Origin Resource Sharing
- **Comprehensive Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Error Handling**: Detailed error responses with proper HTTP status codes
- **Logging**: Structured logging for monitoring and debugging
- **Testing**: Comprehensive test suite using pytest
- **Security**: Password hashing, JWT tokens, input sanitization
- **Middleware**: Request timing, CORS, trusted hosts, and rate limiting
- **API Versioning**: Clean URL versioning structure

## 📁 Project Structure

```
generative_ai_project/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application with middleware
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Application configuration
│   │   └── security.py         # JWT and password utilities
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py             # API dependencies (auth, etc.)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py          # API router configuration
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── users.py    # User CRUD endpoints
│   │           └── items.py    # Item CRUD endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # User data models
│   │   └── item.py             # Item data models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py             # User request/response schemas
│   │   └── item.py             # Item request/response schemas
│   └── services/
│       ├── __init__.py
│       ├── user_service.py     # User business logic
│       └── item_service.py     # Item business logic
├── tests/
│   ├── __init__.py
│   └── test_main.py            # Comprehensive test suite
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd generative_ai_project
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate virtual environment
# On Windows:
venv\\Scripts\\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Copy the `.env` file and modify settings as needed:

```bash
cp .env .env.local
```

**Important**: Change the `SECRET_KEY` in production!

```env
SECRET_KEY="your-super-secure-secret-key-here"
DEBUG=false
```

### 5. Run the Application

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
cd app
python main.py
```

The API will be available at:
- **Main API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔧 Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_main.py
```

## 📚 API Documentation

### Authentication

The API uses JWT Bearer token authentication. Here's how to get started:

#### 1. Register a New User

```bash
curl -X POST \"http://localhost:8000/api/v1/users/register\" \
  -H \"Content-Type: application/json\" \
  -d '{
    \"email\": \"user@example.com\",
    \"username\": \"testuser\",
    \"full_name\": \"Test User\",
    \"password\": \"SecurePass123\"
  }'
```

#### 2. Login to Get Access Token

```bash
curl -X POST \"http://localhost:8000/api/v1/users/login\" \
  -H \"Content-Type: application/json\" \
  -d '{
    \"username\": \"testuser\",
    \"password\": \"SecurePass123\"
  }'
```

Response:
```json
{
  \"access_token\": \"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...\",
  \"token_type\": \"bearer\",
  \"expires_in\": 1800
}
```

#### 3. Use the Token in Requests

```bash
curl -X GET \"http://localhost:8000/api/v1/users/me\" \
  -H \"Authorization: Bearer <your-access-token>\"
```

### API Endpoints

#### Health & Information
- `GET /` - API root information
- `GET /health` - Health check endpoint

#### User Management
- `POST /api/v1/users/register` - Register new user
- `POST /api/v1/users/login` - User login
- `GET /api/v1/users/me` - Get current user info
- `PUT /api/v1/users/me` - Update current user
- `GET /api/v1/users/` - List all users (admin only)
- `GET /api/v1/users/{user_id}` - Get user by ID (admin only)
- `PUT /api/v1/users/{user_id}` - Update user by ID (admin only)
- `DELETE /api/v1/users/{user_id}` - Delete user (admin only)

#### Item Management
- `POST /api/v1/items/` - Create new item
- `GET /api/v1/items/` - List all items (with pagination)
- `GET /api/v1/items/my-items` - Get current user's items
- `GET /api/v1/items/{item_id}` - Get item by ID
- `PUT /api/v1/items/{item_id}` - Update item (owner only)
- `DELETE /api/v1/items/{item_id}` - Delete item (owner only)
- `PATCH /api/v1/items/{item_id}/status` - Update item status

### Example Usage

#### Create an Item

```bash
curl -X POST \"http://localhost:8000/api/v1/items/\" \
  -H \"Authorization: Bearer <your-token>\" \
  -H \"Content-Type: application/json\" \
  -d '{
    \"title\": \"Awesome Product\",
    \"description\": \"A really awesome product for sale\",
    \"price\": 99.99,
    \"status\": \"active\"
  }'
```

#### Get Items with Pagination

```bash
curl \"http://localhost:8000/api/v1/items/?page=1&size=10&status=active\"
```

## 🔒 Security Features

- **Password Hashing**: Uses bcrypt for secure password storage
- **JWT Tokens**: Stateless authentication with configurable expiration
- **Input Validation**: Comprehensive validation using Pydantic
- **Rate Limiting**: Prevents API abuse with configurable limits
- **CORS Protection**: Configurable cross-origin resource sharing
- **Trusted Hosts**: Middleware to validate incoming requests
- **Error Handling**: Secure error messages that don't leak sensitive information

## ⚙️ Configuration

Key configuration options in `.env`:

```env
# Application
APP_NAME=\"Generative AI FastAPI Demo\"
DEBUG=true

# Security
SECRET_KEY=\"your-secret-key\"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# CORS
ALLOWED_ORIGINS=[\"http://localhost:3000\"]

# Logging
LOG_LEVEL=\"INFO\"
```

## 🚀 Deployment

### Docker Deployment (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY .env .

EXPOSE 8000

CMD [\"uvicorn\", \"app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]
```

Build and run:
```bash
docker build -t fastapi-demo .
docker run -p 8000:8000 fastapi-demo
```

### Production Deployment

1. **Set environment variables**:
   - Change `SECRET_KEY` to a secure random string
   - Set `DEBUG=false`
   - Configure `ALLOWED_ORIGINS` for your domain

2. **Use a production ASGI server**:
   ```bash
   pip install gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

3. **Set up reverse proxy** (nginx, Apache, etc.)

4. **Use a real database** (PostgreSQL, MySQL, etc.)

## 🧪 Testing

The project includes comprehensive tests covering:

- **Endpoint Testing**: All API endpoints with various scenarios
- **Authentication**: Login, registration, token validation
- **Authorization**: Permission checks for protected endpoints
- **Validation**: Input validation and error handling
- **Rate Limiting**: API abuse prevention
- **Error Cases**: 404s, 401s, validation errors

Run specific test categories:
```bash
# Test user endpoints only
pytest tests/test_main.py::TestUserEndpoints -v

# Test with coverage report
pytest --cov=app --cov-report=html tests/
```

## 🔄 API Versioning

The API uses URL-based versioning:
- Current version: `/api/v1/`
- Future versions: `/api/v2/`, etc.

This allows for backward compatibility when introducing breaking changes.

## 📝 Development

### Code Style

The project follows Python best practices:

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint code
flake8 app/ tests/

# Type checking
mypy app/
```

### Adding New Endpoints

1. Create schemas in `app/schemas/`
2. Create models in `app/models/`
3. Implement service logic in `app/services/`
4. Create endpoints in `app/api/v1/endpoints/`
5. Add to router in `app/api/v1/api.py`
6. Write tests in `tests/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass (`pytest`)
6. Format your code (`black app/ tests/`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Documentation**: Visit http://localhost:8000/docs when running locally
- **Issues**: Report issues on the project repository
- **API Support**: Check the comprehensive OpenAPI documentation

## 🎯 Key Learning Points

This project demonstrates:

1. **Clean Architecture**: Separation of concerns with models, schemas, services, and endpoints
2. **Security Best Practices**: JWT authentication, password hashing, input validation
3. **API Design**: RESTful endpoints with proper HTTP status codes
4. **Documentation**: Auto-generated, comprehensive API documentation
5. **Testing**: Thorough test coverage with pytest
6. **Configuration Management**: Environment-based configuration
7. **Error Handling**: Graceful error handling with detailed responses
8. **Performance**: Rate limiting and efficient async operations
9. **Scalability**: Clean code structure that supports growth
10. **Production Readiness**: Logging, monitoring, security considerations

---

**Happy coding!** 🎉