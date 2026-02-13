from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
import os
from contextlib import asynccontextmanager
import asyncio
import logging
from dotenv import load_dotenv

from .models import BaseModel
from .database import db_engine
from .routers import health_check, oauth, auth

load_dotenv()  # Load environment variables from .env file

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for the FastAPI application. This function is called during the startup and shutdown of the application.
    
    :param app: The FastAPI application instance.
    :type app: FastAPI
    """
    # Perform any startup tasks here (e.g., database connection, cache initialization)
    logging.info("Starting up XPay application...")
    await asyncio.to_thread(BaseModel.metadata.create_all, bind=db_engine)
    yield
    # Perform any shutdown tasks here (e.g., closing database connections, clearing caches)
    logging.info("Shutting down XPay application...")

xpay = FastAPI(lifespan=lifespan)
xpay.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET"),
)
xpay.include_router(health_check.router)
xpay.include_router(oauth.router)
xpay.include_router(auth.router)