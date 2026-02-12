from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..dependencies import get_db
from sqlalchemy.exc import OperationalError

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/backend")
async def backend_health_check():
    """
    Health check endpoint for the backend service. This endpoint can be used to verify that the backend is running and responsive.
    """
    return {"status": "XPay backend is running"}

@router.get("/db")
def db_health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint for the database connection. This endpoint attempts to execute a simple query against the database to verify that the connection is healthy.
    
    :param db: The database session, injected as a dependency for database operations.
    :type db: Session
    """
    try:
        db.execute(text("SELECT 1"))
        return {"status": "Database connection is healthy"}
    except OperationalError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )