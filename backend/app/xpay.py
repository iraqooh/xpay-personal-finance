from fastapi import FastAPI
from .routers import health_check

xpay = FastAPI()
xpay.include_router(health_check.router)