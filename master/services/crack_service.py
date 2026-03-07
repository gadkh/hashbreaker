from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from shared.api import CrackRequest, CrackResponse, StatusResponse
from shared.enums import TaskStatus
from master.db.models.hash_task import HashTask


async def process_crack_request(request: CrackRequest, db: AsyncSession) -> CrackResponse:
    stmt = select(HashTask).where(HashTask.hash_value == request.hash_value)
    result = await db.execute(stmt)
    existing_task = result.scalars().first()

    if existing_task:
        return CrackResponse(
            hash_value=existing_task.hash_value,
            status=existing_task.status,
            message="Hash already exists in the system.",
            password=existing_task.cracked_password
        )

    new_task = HashTask(hash_value=request.hash_value, status=TaskStatus.PROCESSING)
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    # TODO: await dispatch_crack_task(request.hash_value)

    return CrackResponse(
        hash_value=new_task.hash_value,
        status=new_task.status,
        message="Task accepted and processing started."
    )


async def get_task_status(hash_value: str, db: AsyncSession) -> StatusResponse | None:

    stmt = select(HashTask).where(HashTask.hash_value == hash_value)
    result = await db.execute(stmt)
    task = result.scalars().first()

    if not task:
        return None

    return StatusResponse(
        hash_value=task.hash_value,
        status=task.status,
        password=task.cracked_password
    )