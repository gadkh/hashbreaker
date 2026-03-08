from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from master.services.hash_manager import dispatch_crack_task
from shared.api import CrackRequest, CrackResponse, StatusResponse
from shared.enums import TaskStatus
from shared.logger import setup_logger
from master.db.models.hash_task import HashTask
from typing import Optional

logger = setup_logger(__name__)


async def get_task_by_hash(hash_value: str, db: AsyncSession) -> Optional[HashTask]:
    stmt = select(HashTask).where(HashTask.hash_value == hash_value)
    result = await db.execute(stmt)
    return result.scalars().first()


async def add_task(hash_value: str, db: AsyncSession) -> HashTask:
    logger.info(f"Adding new task to database for hash: {hash_value}")
    new_task = HashTask(hash_value=hash_value, status=TaskStatus.PROCESSING)
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    logger.info(f"Successfully saved task {hash_value} to database")
    return new_task


async def process_crack_request(request: CrackRequest, db: AsyncSession) -> CrackResponse:
    logger.info(f"Checking if hash {request.hash_value} already exists in the system...")
    existing_task = await get_task_by_hash(request.hash_value, db)
    if existing_task:
        logger.info(f" Hash {request.hash_value} found! Current status: {existing_task.status}")
        return CrackResponse(
            hash_value=existing_task.hash_value,
            status=existing_task.status,
            message="Hash already exists in the system.",
            password=existing_task.cracked_password
        )
    logger.info(f"Hash {request.hash_value} is new. Initiating crack sequence...")
    new_task = await add_task(request.hash_value, db)
    await dispatch_crack_task(request.hash_value)
    logger.info(f"Crack sequence fully dispatched for hash: {request.hash_value}")
    return CrackResponse(
        hash_value=new_task.hash_value,
        status=new_task.status,
        message="Task accepted and processing started."
    )

async def get_task_status(hash_value: str, db: AsyncSession) -> Optional[StatusResponse]:
    logger.debug(f"Checking status for hash: {hash_value}")
    task = await get_task_by_hash(hash_value, db)
    if not task:
        logger.debug(f"Status check failed: Hash {hash_value} not found.")
        return None
    return StatusResponse(
        hash_value=task.hash_value,
        status=task.status,
        password=task.cracked_password
   )