from fastapi import FastAPI
from sqlalchemy import text

xpay = FastAPI()

@xpay.get('/health/backend')
async def health_check():
    return {"status": "XPay backend is running"}

@xpay.get("/health/db")
async def db_health_check():
    try:
        from .database import db_engine
        with db_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "Database connection is healthy"}
    except Exception as e:
        return {"status": "Database connection failed", "error": str(e)}