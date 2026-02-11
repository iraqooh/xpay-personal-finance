from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
import os

from .routers import health_check, oauth

xpay = FastAPI()
xpay.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "8tGK3FlMl6v3yL3H-w61JogAeZH6Rb4u84SGEssNHQM"),
)
xpay.include_router(health_check.router)
xpay.include_router(oauth.router)