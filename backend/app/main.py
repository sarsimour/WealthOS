try:
    import redis.asyncio as redis  # Import redis

    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False
    print("Redis not available - caching and rate limiting will be limited")

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import caching libraries
try:
    from fastapi_cache import FastAPICache
    from fastapi_cache.backends.inmemory import InMemoryBackend

    CACHE_AVAILABLE = True
except ImportError:
    FastAPICache = None
    InMemoryBackend = None
    CACHE_AVAILABLE = False
    print("FastAPI Cache not available - caching will be disabled")

# Import limiter libraries
try:
    from fastapi_limiter import FastAPILimiter

    LIMITER_AVAILABLE = True
except ImportError:
    FastAPILimiter = None
    LIMITER_AVAILABLE = False
    print("FastAPI Limiter not available - rate limiting will be disabled")

from app.api.router import api_router
from app.core.config import settings


# Define lifespan manager for cache and limiter initialization/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Redis connection (shared by cache and limiter if needed)
    redis_connection = None
    if REDIS_AVAILABLE:
        # TODO: Get Redis URL from settings
        redis_url = "redis://localhost"
        try:
            redis_connection = redis.from_url(
                redis_url, encoding="utf8", decode_responses=True
            )
            print(f"Connecting to Redis at {redis_url}...")
            await redis_connection.ping()  # Check connection
            print("Redis connection successful.")
        except Exception as e:
            print(f"!!! Failed to connect to Redis at {redis_url}: {e} !!!")
            print(
                "!!! Rate limiting and potentially Redis-based caching will NOT work. !!!"
            )
            redis_connection = None
    else:
        print("Redis not available - using in-memory alternatives")

    # Initialize Cache (using In-Memory for now, could switch to Redis)
    print("Initializing cache...")
    if CACHE_AVAILABLE:
        FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
        # Example: FastAPICache.init(RedisBackend(redis_connection), prefix="fastapi-cache")
        print("Cache initialized.")
    else:
        print("Cache disabled - FastAPI Cache not available")

    # Initialize Rate Limiter (only if Redis connected)
    if redis_connection and REDIS_AVAILABLE and LIMITER_AVAILABLE:
        print("Initializing rate limiter...")
        await FastAPILimiter.init(redis_connection)
        print("Rate limiter initialized.")
    else:
        print(
            "Skipping rate limiter initialization due to Redis unavailability or missing FastAPI Limiter."
        )

    yield

    # Clean up connections/cache (optional for in-memory)
    if redis_connection:
        await redis_connection.close()
        print("Redis connection closed.")
    print("Cache shutdown.")
    print("Lifespan shutdown complete.")


app = FastAPI(
    title="WealthOS API",
    description="Financial analysis and investment platform API",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Welcome to WealthOS API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
