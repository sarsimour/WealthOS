from fastapi import APIRouter

from app.api.routes import auth, users

# Import endpoint routers
from app.api.v1.endpoints import crypto

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)

# Include v1 endpoints
api_router.include_router(
    crypto.router, prefix="/v1/crypto", tags=["Crypto Market Data"]
)

# Include other routers from v1 or other versions as needed
# api_router.include_router(
#     another_router.router, prefix="/v1/another", tags=["Another"]
# )
