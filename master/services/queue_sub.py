import asyncio
import aio_pika
from sqlalchemy import update
from shared.messages import CrackResult
from shared.enums import TaskStatus
from master.core.config import settings

from master.db.database import AsyncSessionLocal
from master.db.models.hash_task import HashTask



async def process_result_message(message: aio_pika.IncomingMessage):

    async with message.process():
        try:
            result_data = CrackResult.model_validate_json(message.body)

            async with AsyncSessionLocal() as db:
                stmt = (
                    update(HashTask)
                    .where(HashTask.hash_value == result_data.hash_value)
                    .values(
                        status=TaskStatus.COMPLETED,
                        cracked_password=result_data.cracked_password
                    )
                )
                await db.execute(stmt)
                await db.commit()

        except Exception as e:
            print(e)


async def start_results_consumer():

    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    channel = await connection.channel()

    queue = await channel.declare_queue(settings.RESULTS_QUEUE, durable=True)

    await queue.consume(process_result_message)

    try:
        await asyncio.Future()
    finally:
        await connection.close()