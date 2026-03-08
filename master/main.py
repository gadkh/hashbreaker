from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from master.routers.v1 import api_router
from master.db.database import engine
from master.db.models.hash_task import Base
from master.services.queue_sub import start_results_consumer
import asyncio
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Master API initialized. Async DB connected.")
    consumer_task = asyncio.create_task(start_results_consumer())
    print("Started RabbitMQ results consumer.")
    yield
    consumer_task.cancel()
    print("Shutting down Master API...")
    print("Shutting down Master API and background tasks...")


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