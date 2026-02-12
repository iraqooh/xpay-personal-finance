from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.xpay import xpay # Import the FastAPI app instance
from app.dependencies import get_db # Import the database instance

client = TestClient(xpay)

def test_health_backend():
    """
    Test the backend health check endpoint to ensure it returns a healthy status when the backend is running.
    """
    response = client.get("/health/backend")

    assert response.status_code == 200
    assert response.json() == {"status": "XPay backend is running"}

def test_health_db_connected():
    """
    Test the database health check endpoint to ensure it returns a healthy status when the database connection is successful.
    """
    response = client.get("/health/db")

    assert response.status_code == 200
    assert response.json() == {"status": "Database connection is healthy"}

# def test_health_db_failure():
#     # Simulate a database connection failure by patching the get_db dependency
#     def mock_get_db():
#         raise OperationalError("Simulated database connection failure", None, None)

#     #Override the get_db dependency with our mock function that simulates a failure
#     xpay.dependency_overrides[get_db] = mock_get_db

#     response = client.get("/health/db")

#     assert response.status_code == 503
#     assert "Database connection failed" in response.json()["detail"]

#     xpay.dependency_overrides.clear() # Clear the dependency override after the test to avoid affecting other tests