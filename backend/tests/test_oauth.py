from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from urllib.parse import urlparse, parse_qs
import os
from dotenv import load_dotenv

from app.xpay import xpay # Import the FastAPI app instance
from app.core.oauth import oauth_client # Import the OAuth client instance
from app.routers.oauth import router # Import the OAuth router
from app.dependencies import get_db # Import the database dependency

load_dotenv()  # Load environment variables from .env file

client = TestClient(xpay)

def test_oauth_client_is_configured():
    """
    Test that the OAuth client is properly configured with the expected client ID, client secret, and scopes.
    This test checks that the Google OAuth client is initialized with the correct credentials and scopes as defined in the environment variables.
    """
    assert oauth_client.google is not None
    assert oauth_client.google.client_id == os.getenv("GOOGLE_CLIENT_ID")
    assert oauth_client.google.client_secret == os.getenv("GOOGLE_CLIENT_SECRET")
    assert "openid" in oauth_client.google.client_kwargs["scope"]

def test_google_login_redirect():
    """
    Test that the /oauth/google/login endpoint correctly initiates the Google OAuth login flow by redirecting the user to Google's authorization endpoint.
    This test verifies that when a GET request is made to the /oauth/google/login endpoint, the response is a redirect (HTTP 302) to the Google authorization URL, and that the URL contains the expected query parameters for client_id, scope, response_type, and redirect_uri.
    """
    response = client.get("/oauth/google/login", follow_redirects=False) # Don't follow redirects to capture the initial response

    assert response.status_code == 302
    location = response.headers["location"]

    assert "accounts.google.com" in location
    assert "client_id=" in location
    assert "scope=openid+email+profile" in location
    assert "response_type=code" in location
    assert "redirect_uri=" in location

@patch("app.core.oauth.oauth_client.google.authorize_access_token") # Mock the token exchange method to simulate a successful token exchange with Google during the OAuth callback
@patch("app.core.oauth.oauth_client.google.userinfo") # Mock the user info retrieval method to simulate fetching user information from Google during the OAuth callback
def test_google_callback_creates_new_user(
    mock_userinfo: AsyncMock,
    mock_get_token: AsyncMock
):
    """
    Test the /auth/google/callback endpoint to ensure it correctly handles the OAuth callback from Google, processes the authorization response, and creates a new user in the database if the user does not already exist.
    This test simulates the OAuth callback by mocking the token exchange and user info retrieval to return a new user's information. It also mocks the database session to simulate an empty database (no existing user). The test verifies that the endpoint responds with a redirect containing an access token, indicating a successful login and user creation.
    
    :param mock_userinfo: Mock object for simulating the user info retrieval from Google during the OAuth callback.
    :type mock_userinfo: AsyncMock
    :param mock_get_token: Mock object for simulating the token exchange with Google during the OAuth callback.
    :type mock_get_token: AsyncMock
    """
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
        """
        Mock database session that simulates an empty database (no existing user). This mock class provides the necessary methods to mimic the behavior of a SQLAlchemy session for the purposes of testing the OAuth callback endpoint.
        The mock session includes methods for querying the User model, filtering results, and simulating the addition and commitment of new user records to the database. This allows the test to verify that a new user is created when the OAuth callback is processed with user information that does not already exist in the database.
        """
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
    
    # Override the get_db dependency with our mock function that simulates an empty database
    xpay.dependency_overrides[get_db] = mock_get_db

    # Simulate the callback from Google with a fake authorization code and state
    response = client.get(
        "/oauth/google/callback?code=fake-code&state=fake-state", 
        follow_redirects=False
    )

    assert response.status_code == 307
    location = response.headers["location"]

    # Check that the redirect URL contains a token or access token, indicating successful login
    assert "?token=" in location or "access_token" in location

    xpay.dependency_overrides[get_db] = mock_get_db

    response = client.get(
        "/oauth/google/callback?code=fake-code&state=fake-state",
        follow_redirects=False
    )
    assert response.status_code == 307
    assert "access_token=" in response.headers["location"]

    xpay.dependency_overrides.clear()

@patch("app.core.oauth.oauth_client.google.authorize_access_token", new_callable=AsyncMock)
@patch("app.core.oauth.oauth_client.google.userinfo", new_callable=AsyncMock)
def test_google_callback_existing_user(mock_userinfo, mock_get_token):
    """
    Test the /auth/google/callback endpoint to ensure it correctly handles the OAuth callback from Google when the user already exists in the database.
    This test simulates the OAuth callback by mocking the token exchange and user info retrieval to return
    information for an existing user. It also mocks the database session to simulate an existing user in the database. The test verifies that the endpoint responds with a redirect containing an access token, indicating a successful login without creating a new user.
    
    :param mock_userinfo: Mock object for simulating the user info retrieval from Google during the OAuth callback.
    :type mock_userinfo: AsyncMock
    """
    mock_get_token.return_value = {"access_token": "fake-token"}
    mock_userinfo.return_value = {"sub": "google123", "email": "existing@example.com", "name": "Existing User"}

    # Mock DB session with an existing user
    def mock_get_db_existing_user():
        """
        Mock database session that simulates an existing user in the database. This mock class provides the necessary methods to mimic the behavior of a SQLAlchemy session for the purposes of testing the OAuth callback endpoint when a user already exists.
        The mock session includes methods for querying the User model, filtering results, and simulating the retrieval of an existing user record from the database. This allows the test to verify that when the OAuth callback is processed with user information that already exists in the database, the existing user is recognized and no new user is created.
        """
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
    
    xpay.dependency_overrides[get_db] = mock_get_db_existing_user

    response = client.get("/oauth/google/callback?code=fake-code&state=fake-state", follow_redirects=False)
    assert response.status_code == 307
    assert "access_token=" in response.headers["location"]

    xpay.dependency_overrides.clear()