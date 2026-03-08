import asyncio
import aio_pika
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from shared.messages import CrackResult
from shared.enums import TaskStatus
from shared.logger import setup_logger
from master.core.config import settings
from master.db.database import AsyncSessionLocal
from master.db.models.hash_task import HashTask
import redis.asyncio as aioredis

logger = setup_logger(__name__)

redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)


async def update_not_found(result_data:CrackResult, db: AsyncSession) -> None:
    logger.warning(f"Received NOT_FOUND signal for hash {result_data.hash_value}")
    stmt = (
        update(HashTask)
        .where(HashTask.hash_value == result_data.hash_value)
        .values(status=TaskStatus.NOT_FOUND)
    )
    await db.execute(stmt)
    await db.commit()
    logger.info(f"Database updated to NOT_FOUND for hash {result_data.hash_value}")


async def update_completed(result_data:CrackResult, db: AsyncSession) -> None:
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
    logger.info(f"Database successfully updated to COMPLETED for hash {result_data.hash_value}")
    await set_redis(result_data)


async def set_redis(result_data: CrackResult) -> None:
    await redis_client.set(
        f"hash_status:{result_data.hash_value}",
        "COMPLETED",
        ex=86400
    )
    logger.info(f"Redis flag set: Minions will abort work for hash {result_data.hash_value}")


async def process_result_message(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            result_data = CrackResult.model_validate_json(message.body)
            logger.info(f"Received cracked result for hash {result_data.hash_value}")
            logger.info(f"Password found: {result_data.cracked_password}")
            async with AsyncSessionLocal() as db:
                if result_data.not_found:
                    await update_not_found(result_data, db)

                else:
                    await update_completed(result_data, db)
                    await set_redis(result_data)
        except Exception as e:
            logger.error(f"Error processing result message: {e}", exc_info=True)


async def start_results_consumer():
    try:
        logger.info("Starting RabbitMQ Results Consumer...")
        connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        channel = await connection.channel()
        queue = await channel.declare_queue(settings.RESULTS_QUEUE, durable=True)
        logger.info("Starting RabbitMQ Results Consumer...")
        await queue.consume(process_result_message)
        try:
            await asyncio.Future()
        finally:
            logger.info("Closing RabbitMQ connection for Results Consumer.")
            await connection.close()
    except Exception as e:
        logger.error(f"Failed to start Results Consumer: {e}", exc_info=True)