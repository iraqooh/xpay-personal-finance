from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, event
import os
from dotenv import load_dotenv

from app.xpay import xpay
from app.core.security import get_password_hash
from app.models import User, BaseModel
from app.dependencies import get_db

# ── Use test DB BEFORE app starts ────────────────────────────────────────────

load_dotenv()
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL environment variable must be set for tests")

engine = create_engine(
    TEST_DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False)


# ── Create schema once for all tests ─────────────────────────────────────────

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """This fixture sets up the test database schema before any tests are run and tears it down after all tests have completed. It ensures that the database schema is created once for the entire test session, providing a consistent and isolated environment for all tests that interact with the database.
    """
    BaseModel.metadata.create_all(bind=engine)
    yield
    BaseModel.metadata.drop_all(bind=engine)


# ── Transaction-per-test isolation ──────────────────────────────────────────

@pytest.fixture
def db():
    """
    This fixture provides a database session for each test, ensuring that each test runs within a transaction that is rolled back after the test completes. This allows tests to interact with the database without affecting other tests, maintaining isolation and ensuring a clean state for each test.
    
    :yield: A SQLAlchemy Session object that can be used to interact with the database during a test.
    :rtype: Session
    """
    connection = engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)

    # Begin a SAVEPOINT (nested transaction)
    nested = connection.begin_nested()

    # Re-create SAVEPOINT after each commit inside the session
    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction_):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# ── Override FastAPI DB dependency to use SAME session ──────────────────────

@pytest.fixture
def client(db: Session):
    """
    This fixture provides a TestClient instance for testing the FastAPI application, with the database dependency overridden to use the same database session for each test. This allows tests to interact with the database in a consistent and isolated manner, ensuring that changes made during a test do not affect other tests.
    
    :param db: The database session provided by the db fixture, which is used to override the get_db dependency in the FastAPI application.
    :type db: Session
    """

    def override_get_db():
        try:
            yield db
        finally:
            pass

    xpay.dependency_overrides[get_db] = override_get_db

    with TestClient(xpay) as c:
        yield c

    xpay.dependency_overrides.clear()


# ── Test user fixture ───────────────────────────────────────────────────────

@pytest.fixture
def test_user(db: Session):
    """This fixture creates a test user in the database with known credentials that can be used for testing authentication-related functionality, such as registration and login. The fixture adds a user with a specific email, full name, and hashed password to the database, and returns the created user object for use in tests that require an existing user.
    
    :param db: The database session used to interact with the database for creating the test user.
    :type db: Session
    """
    user = User(
        email="daryna@neotopia.com",
        full_name="Daryna Johnston",
        hashed_password=get_password_hash("daryna123"),
        is_active=True
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ── Register tests ──────────────────────────────────────────────────────────

def test_register_success(client):
    """
    This test verifies that a new user can successfully register. It sends a POST request to the /auth/register endpoint with valid user information, and asserts that the response status code is 201 Created. The test also checks that the response contains an access token, the correct token type (bearer), and that the user information in the response matches the input email.

    :param client: The TestClient instance used to make requests to the FastAPI application.
    :type client: TestClient
    """
    payload = {
        "email": "ruslana@neotopia.com",
        "full_name": "Ruslana Johnston",
        "password": "testpassword123"
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == payload["email"]


def test_register_duplicate_email(client, test_user):
    """
    This test verifies that attempting to register with an email that is already in use results in a 400 Bad Request response with the appropriate error message indicating that the email is already registered.

    :param client: The TestClient instance used to make requests to the FastAPI application.
    :type client: TestClient
    :param test_user: The test user fixture that provides a user with known credentials for testing the registration functionality, including the case of duplicate email registration.
    :type test_user: User
    """
    payload = {
        "email": test_user.email,
        "full_name": "Duplicate User",
        "password": "testpassword123"
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


# ── Login tests ─────────────────────────────────────────────────────────────

def test_login_success(client, test_user):
    """
    This test verifies that a user can successfully log in with valid credentials. It sends a POST request to the /auth/login endpoint with the test user's email and password, and asserts that the response status code is 200 OK. The test also checks that the response contains an access token, the correct token type (bearer), and that the user information in the response matches the test user's email.

    :param client: The TestClient instance used to make requests to the FastAPI application.
    :type client: TestClient
    :param test_user: The test user fixture that provides a user with known credentials for testing the login functionality.
    :type test_user: User
    """
    form_data = {
        "username": test_user.email,
        "password": "daryna123"
    }

    response = client.post("/auth/login", data=form_data)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == test_user.email


def test_login_invalid_credentials(client, test_user):
    """This test verifies that attempting to log in with an incorrect password results in a 401 Unauthorized response with the appropriate error message indicating invalid email or password.
    
    :param client: The TestClient instance used to make requests to the FastAPI application.
    :type client: TestClient
    """
    form_data = {
        "username": test_user.email,
        "password": "wrongpassword"
    }

    response = client.post("/auth/login", data=form_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_nonexistent_user(client):
    """
    This test verifies that attempting to log in with credentials that do not correspond to any existing user results in a 401 Unauthorized response with the appropriate error message indicating invalid email or password.
    
    :param client: The TestClient instance used to make requests to the FastAPI application.
    :type client: TestClient
    """
    form_data = {
        "username": "doesnotexist@example.com",
        "password": "Irrelevant123"
    }

    response = client.post("/auth/login", data=form_data)

    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_inactive_user(client, db: Session):
    """
    This test verifies that an inactive user cannot log in. It creates a user with the is_active flag set to False, attempts to log in with that user's credentials, and asserts that the response status code is 401 Unauthorized with the appropriate error message indicating invalid email or password.

    :param client: The TestClient instance used to make requests to the FastAPI application.
    :type client: TestClient
    """
    inactive_user = User(
        email="inactive@example.com",
        full_name="Inactive User",
        hashed_password=get_password_hash("Pass123!"),
        is_active=False
    )

    db.add(inactive_user)
    db.commit()

    form_data = {
        "username": "inactive@example.com",
        "password": "Pass123!"
    }

    response = client.post("/auth/login", data=form_data)

    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]