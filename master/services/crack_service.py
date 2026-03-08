from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from master.services.hash_manager import dispatch_crack_task
from shared.api import CrackRequest, CrackResponse, StatusResponse
from shared.enums import TaskStatus
from master.db.models.hash_task import HashTask
from typing import Optional


async def get_task_by_hash(hash_value: str, db: AsyncSession) -> Optional[HashTask]:
    stmt = select(HashTask).where(HashTask.hash_value == hash_value)
    result = await db.execute(stmt)
    return result.scalars().first()


async def add_task(hash_value: str, db: AsyncSession) -> HashTask:
    new_task = HashTask(hash_value=hash_value, status=TaskStatus.PROCESSING)
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task


async def process_crack_request(request: CrackRequest, db: AsyncSession) -> CrackResponse:
    existing_task = await get_task_by_hash(request.hash_value, db)
    if existing_task:
        return CrackResponse(
            hash_value=existing_task.hash_value,
            status=existing_task.status,
            message="Hash already exists in the system.",
            password=existing_task.cracked_password
        )
    new_task = await add_task(request.hash_value, db)
    await dispatch_crack_task(request.hash_value)
    return CrackResponse(
        hash_value=new_task.hash_value,
        status=new_task.status,
        message="Task accepted and processing started."
    )

async def get_task_status(hash_value: str, db: AsyncSession) -> Optional[StatusResponse]:
    task = await get_task_by_hash(hash_value, db)
    if not task:
        return None
    return StatusResponse(
        hash_value=task.hash_value,
        status=task.status,
        password=task.cracked_password
   )



# async def process_crack_request(request: CrackRequest, db: AsyncSession) -> CrackResponse:
#     # stmt = select(HashTask).where(HashTask.hash_value == request.hash_value)
#     # result = await db.execute(stmt)
#     # existing_task = result.scalars().first()
#
#     existing_task = await get_task_by_hash(request.hash_value, db)
#
#     if existing_task:
#         return CrackResponse(
#             hash_value=existing_task.hash_value,
#             status=existing_task.status,
#             message="Hash already exists in the system.",
#             password=existing_task.cracked_password
#         )
#
#     new_task = HashTask(hash_value=request.hash_value, status=TaskStatus.PROCESSING)
#     db.add(new_task)
#     await db.commit()
#     await db.refresh(new_task)
#
#     await dispatch_crack_task(request.hash_value)
#
#     return CrackResponse(
#         hash_value=new_task.hash_value,
#         status=new_task.status,
#         message="Task accepted and processing started."
#     )


# async def get_task_status(hash_value: str, db: AsyncSession) -> Optional[StatusResponse]:
#
#     # stmt = select(HashTask).where(HashTask.hash_value == hash_value)
#     # result = await db.execute(stmt)
#     # task = result.scalars().first()
#
#     task = await get_task_by_hash(hash_value, db)
#
#     if not task:
#         return None
#
#     return StatusResponse(
#         hash_value=task.hash_value,
#         status=task.status,
#         password=task.cracked_password
#    )
