from fastapi import APIRouter

from app.api.routes import auth, users

# Import endpoint routers
# Import the new prices router
from app.api.v1.endpoints import crypto, market_data, prices

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)

# Include v1 endpoints
api_router.include_router(
    crypto.router, prefix="/v1/crypto", tags=["Crypto Market Data"]
)
# Include the new prices router
api_router.include_router(prices.router, prefix="/v1/prices", tags=["Prices"])

# Include the market_data router
api_router.include_router(
    market_data.router, prefix="/v1/market-data", tags=["Market Data"]
)

# Include other routers from v1 or other versions as needed
# api_router.include_router(
#     another_router.router, prefix="/v1/another", tags=["Another"]
# )
