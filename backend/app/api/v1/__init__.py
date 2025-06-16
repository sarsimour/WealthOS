from fastapi import APIRouter
from .endpoints import price

api_router = APIRouter()

# Include price endpoints
api_router.include_router(price.router)
