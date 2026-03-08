from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from master.routers.v1 import api_router
from master.db.database import engine
from master.db.models.hash_task import Base
from master.services.queue_sub import start_results_consumer
from shared.logger import setup_logger
import asyncio
import uvicorn


logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting HashBreaker Master Service...")
    logger.info("Initializing Database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Starting RabbitMQ Consumer in the background...")
    consumer_task = asyncio.create_task(start_results_consumer())
    yield
    consumer_task.cancel()
    logger.info("Shutting down Master API...")
    logger.info("Shutting down Master API and background tasks...")


app = FastAPI(
    title="HashBreaker Master API",
    description="Distributed MD5 Hash Cracker - Master Node",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("master.main:app", host="0.0.0.0", port=8000, reload=True)