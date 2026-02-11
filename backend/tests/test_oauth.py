from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from urllib.parse import urlparse, parse_qs
import os

from app.xpay import xpay # Import the FastAPI app instance
from app.core.oauth import oauth_client # Import the OAuth client instance
from app.routers.oauth import router # Import the OAuth router
from app.dependencies import get_db # Import the database dependency

client = TestClient(xpay)

def test_oauth_client_is_configured():
    assert oauth_client.google is not None
    assert oauth_client.google.client_id == os.getenv("GOOGLE_CLIENT_ID")
    assert oauth_client.google.client_secret == os.getenv("GOOGLE_CLIENT_SECRET")
    assert "openid" in oauth_client.google.client_kwargs["scope"]

def test_google_login_redirect():
    response = client.get("/auth/google/login", follow_redirects=False) # Don't follow redirects to capture the initial response

    assert response.status_code == 302
    location = response.headers["location"]

    assert "accounts.google.com" in location
    assert "client_id=" in location
    assert "scope=openid+email+profile" in location
    assert "response_type=code" in location
    assert "redirect_uri=" in location

@patch("app.core.oauth.oauth_client.google.authorize_access_token")
@patch("app.core.oauth.oauth_client.google.userinfo")
def test_google_callback_new_user(
    mock_userinfo: AsyncMock,
    mock_get_token: AsyncMock,
    monkeypatch
):
    # Mock the token exchange and user info retrieval to simulate a successful OAuth flow
    mock_get_token.return_value = {"access_token": "fake-token"}

    # Mock user info to simulate a new user logging in with Google
    mock_userinfo.return_value = {
        "sub": "google123",
        "email": "testuser@gmail.com",
        "name": "Test User"
    }

    # Mock the database session to simulate no existing user in the database
    def mock_get_db():
        class MockDB:
            def query(self, model):
                return self
            def filter(self, condition):
                return self
            def first(self):
                return None # Simulate no existing user in the database
            def add(self, instance):
                pass
            def commit(self):
                pass
            def refresh(self, instance):
                instance.id = 1 # Simulate the database assigning an ID to the new user
                return instance
        return MockDB()
    
    def mock_get_db_existing_user():
        class MockDB:
            def query(self, model):
                return self
            def filter(self, condition):
                return self
            def first(self):
                class User:
                    id = 42
                    email = "existing@example.com"
                    full_name = "Existing User"
                return User()  # Simulate user already exists
        return MockDB()
    
    # Override the get_db dependency with our mock function that simulates an empty database
    xpay.dependency_overrides[get_db] = mock_get_db

    # Simulate the callback from Google with a fake authorization code and state
    response = client.get(
        "/auth/google/callback?code=fake-code&state=fake-state", 
        follow_redirects=False
    )

    assert response.status_code == 307
    location = response.headers["location"]

    # Check that the redirect URL contains a token or access token, indicating successful login
    assert "?token=" in location or "access_token" in location

    xpay.dependency_overrides[get_db] = mock_get_db_existing_user

    response = client.get(
        "/auth/google/callback?code=fake-code&state=fake-state",
        follow_redirects=False
    )
    assert response.status_code == 307
    assert "access_token=" in response.headers["location"]

    xpay.dependency_overrides.clear()

