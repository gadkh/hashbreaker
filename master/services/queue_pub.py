import aio_pika
from typing import List
from shared.messages import ChunkTask
from master.core.config import settings

async def publish_tasks(tasks: List[ChunkTask]):

    try:
        connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()
            await channel.declare_queue(settings.JOBS_QUEUE, durable=True)

            for task in tasks:
                message = aio_pika.Message(
                    body=task.model_dump_json().encode('utf-8'),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                )
                await channel.default_exchange.publish(
                    message,
                    routing_key=settings.JOBS_QUEUE
                )
    except Exception as e:
        raise e