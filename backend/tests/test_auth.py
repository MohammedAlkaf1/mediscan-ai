"""
Tests for authentication functionality
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from main import app
from database import Base, get_db
from models import User
import auth

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override database dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_password_hashing():
    """Test password hashing and verification"""
    password = "testpassword123"
    hashed = auth.get_password_hash(password)
    
    assert hashed != password
    assert auth.verify_password(password, hashed)
    assert not auth.verify_password("wrongpassword", hashed)


def test_create_access_token():
    """Test JWT token creation and decoding"""
    data = {"sub": "user-id-123", "email": "test@example.com"}
    token = auth.create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    
    # Decode token
    token_data = auth.decode_access_token(token)
    assert token_data is not None
    assert token_data.user_id == "user-id-123"
    assert token_data.email == "test@example.com"


def test_decode_invalid_token():
    """Test decoding an invalid token"""
    invalid_token = "invalid.token.here"
    token_data = auth.decode_access_token(invalid_token)
    assert token_data is None


def test_register_user():
    """Test user registration endpoint"""
    response = client.post(
        "/api/auth/register",
        json={"email": "newuser@example.com", "password": "password123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "created_at" in data
    assert "password" not in data


def test_register_duplicate_email():
    """Test registering with an already used email"""
    # Register first user
    client.post(
        "/api/auth/register",
        json={"email": "duplicate@example.com", "password": "password123"}
    )
    
    # Try to register again with same email
    response = client.post(
        "/api/auth/register",
        json={"email": "duplicate@example.com", "password": "password456"}
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_register_invalid_email():
    """Test registration with invalid email format"""
    response = client.post(
        "/api/auth/register",
        json={"email": "notanemail", "password": "password123"}
    )
    
    assert response.status_code == 400
    assert "invalid email" in response.json()["detail"].lower()


def test_register_short_password():
    """Test registration with password that's too short"""
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "12345"}
    )
    
    assert response.status_code == 400
    assert "6 characters" in response.json()["detail"].lower()


def test_login_success():
    """Test successful login"""
    # Register user first
    client.post(
        "/api/auth/register",
        json={"email": "logintest@example.com", "password": "password123"}
    )
    
    # Login
    response = client.post(
        "/api/auth/login",
        json={"email": "logintest@example.com", "password": "password123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    """Test login with incorrect password"""
    # Register user
    client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "password123"}
    )
    
    # Login with wrong password
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"}
    )
    
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_login_nonexistent_user():
    """Test login with non-existent user"""
    response = client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "password123"}
    )
    
    assert response.status_code == 401


def test_get_current_user():
    """Test getting current user information"""
    # Register and login
    client.post(
        "/api/auth/register",
        json={"email": "currentuser@example.com", "password": "password123"}
    )
    
    login_response = client.post(
        "/api/auth/login",
        json={"email": "currentuser@example.com", "password": "password123"}
    )
    
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "currentuser@example.com"


def test_get_current_user_without_token():
    """Test accessing protected endpoint without token"""
    response = client.get("/api/auth/me")
    
    assert response.status_code == 401


def test_get_current_user_invalid_token():
    """Test accessing protected endpoint with invalid token"""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalidtoken"}
    )
    
    assert response.status_code == 401


def test_upload_report_with_auth():
    """Test uploading a report while authenticated"""
    # Register and login
    client.post(
        "/api/auth/register",
        json={"email": "uploader@example.com", "password": "password123"}
    )
    
    login_response = client.post(
        "/api/auth/login",
        json={"email": "uploader@example.com", "password": "password123"}
    )
    
    token = login_response.json()["access_token"]
    
    # Create a mock file
    files = {"file": ("test.jpg", b"fake image content", "image/jpeg")}
    data = {"save_report": "false"}
    
    response = client.post(
        "/api/reports/upload",
        files=files,
        data=data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "queued"


def test_list_reports_user_specific():
    """Test that users only see their own reports"""
    # Create first user and upload
    client.post(
        "/api/auth/register",
        json={"email": "user1@example.com", "password": "password123"}
    )
    
    login1 = client.post(
        "/api/auth/login",
        json={"email": "user1@example.com", "password": "password123"}
    )
    token1 = login1.json()["access_token"]
    
    # Create demo report for user 1
    client.post(
        "/api/reports/demo",
        headers={"Authorization": f"Bearer {token1}"}
    )
    
    # Create second user and upload
    client.post(
        "/api/auth/register",
        json={"email": "user2@example.com", "password": "password123"}
    )
    
    login2 = client.post(
        "/api/auth/login",
        json={"email": "user2@example.com", "password": "password123"}
    )
    token2 = login2.json()["access_token"]
    
    # Get reports for user 1
    response1 = client.get(
        "/api/reports",
        headers={"Authorization": f"Bearer {token1}"}
    )
    
    # Get reports for user 2
    response2 = client.get(
        "/api/reports",
        headers={"Authorization": f"Bearer {token2}"}
    )
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    user1_reports = response1.json()
    user2_reports = response2.json()
    
    # User 1 should have 1 report, user 2 should have 0
    assert len(user1_reports) == 1
    assert len(user2_reports) == 0


def test_access_other_user_report():
    """Test that users cannot access other users' reports"""
    # Create user 1 and demo report
    client.post(
        "/api/auth/register",
        json={"email": "user1@example.com", "password": "password123"}
    )
    
    login1 = client.post(
        "/api/auth/login",
        json={"email": "user1@example.com", "password": "password123"}
    )
    token1 = login1.json()["access_token"]
    
    demo_response = client.post(
        "/api/reports/demo",
        headers={"Authorization": f"Bearer {token1}"}
    )
    report_id = demo_response.json()["id"]
    
    # Create user 2
    client.post(
        "/api/auth/register",
        json={"email": "user2@example.com", "password": "password123"}
    )
    
    login2 = client.post(
        "/api/auth/login",
        json={"email": "user2@example.com", "password": "password123"}
    )
    token2 = login2.json()["access_token"]
    
    # Try to access user 1's report as user 2
    response = client.get(
        f"/api/reports/{report_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    
    assert response.status_code == 403
    assert "access denied" in response.json()["detail"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
