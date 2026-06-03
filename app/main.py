from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.v1.router import router
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base
from app.middleware.rate_limiting import rate_limit_middleware
from app.core.cache import cache
from app.core.message_queue import message_queue

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Connect to external services
    try:
        await cache._ensure_connection()
        await message_queue.connect()
    except Exception as e:
        print(f"Warning: Could not connect to external services: {e}")

    yield
    # Shutdown
    await message_queue.close()
    await cache.close()

app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.middleware("http")(rate_limit_middleware)

app.include_router(router, prefix="/api/v1")