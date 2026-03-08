import aio_pika
from typing import List
from shared.messages import ChunkTask
from shared.logger import setup_logger
from master.core.config import settings

logger = setup_logger(__name__)

async def publish_tasks(tasks: List[ChunkTask]):
    logger.info("Attempting to connect to RabbitMQ...")
    try:
        connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()
            await channel.declare_queue(settings.JOBS_QUEUE, durable=True)
            logger.info(f"Connected! Publishing {len(tasks)} tasks to queue '{settings.JOBS_QUEUE}'...")

            for task in tasks:
                message = aio_pika.Message(
                    body=task.model_dump_json().encode('utf-8'),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                )
                await channel.default_exchange.publish(
                    message,
                    routing_key=settings.JOBS_QUEUE
                )
                logger.info(f"Successfully published all {len(tasks)} tasks to RabbitMQ.")
    except Exception as e:
        logger.error(f"Failed to publish tasks to RabbitMQ: {e}")
        raise e