from fastapi import APIRouter
from . import crack, health

api_router = APIRouter(prefix="/api")

api_router.include_router(crack.router)
api_router.include_router(health.router)