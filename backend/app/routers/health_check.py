from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..dependencies import get_db
from sqlalchemy.exc import OperationalError

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/backend")
async def backend_health_check():
    return {"status": "XPay backend is running"}

@router.get("/db")
def db_health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "Database connection is healthy"}
    except OperationalError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )