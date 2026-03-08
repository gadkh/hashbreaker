from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
import os
from master.core.config import settings

#DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/hashbreaker")

engine = create_async_engine(
    # DATABASE_URL,
    settings.SQLALCHEMY_DATABASE_URI,
    echo=False,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

Base = declarative_base()

async def get_session() :
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()