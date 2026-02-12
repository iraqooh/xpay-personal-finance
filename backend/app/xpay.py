from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
import os
from contextlib import asynccontextmanager

from .models import BaseModel
from .database import db_engine
from .routers import health_check, oauth

@asynccontextmanager
async def lifespan(xpay: FastAPI):
    # Perform any startup tasks here (e.g., database connection, cache initialization)
    print("Starting up XPay application...")
    BaseModel.metadata.create_all(bind=db_engine) # Create database tables based on the defined models
    yield
    # Perform any shutdown tasks here (e.g., closing database connections, clearing caches)
    print("Shutting down XPay application...")

xpay = FastAPI(lifespan=lifespan)
xpay.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "8tGK3FlMl6v3yL3H-w61JogAeZH6Rb4u84SGEssNHQM"),
)
xpay.include_router(health_check.router)
xpay.include_router(oauth.router)