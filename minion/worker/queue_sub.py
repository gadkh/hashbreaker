import pika
import json
import redis
from pydantic import ValidationError
from minion.core.config import settings
from minion.worker.cracker import crack_chunk
from shared.messages import ChunkTask, CrackResult
from shared.logger import setup_logger

logger = setup_logger(__name__)

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


def process_message(ch, method, properties, body):
    try:
        task_data = json.loads(body)
        task = ChunkTask(**task_data)
        logger.info(
            f"[Minion {settings.MINION_ID}] Picked up task for hash {task.hash_value} | Prefix '{task.prefix}' ({task.start_range}-{task.end_range})")

        result_password = crack_chunk(
            target_hash=task.hash_value,
            prefix=task.prefix,
            start_range=task.start_range,
            end_range=task.end_range
        )

        if result_password:
            logger.info(f"[Minion {settings.MINION_ID}] SUCCESS! Publishing cracked password to '{settings.RESULTS_QUEUE}'")
            result_msg = CrackResult(
                hash_value=task.hash_value,
                cracked_password=result_password,
                minion_id=settings.MINION_ID
            )

            ch.basic_publish(
                exchange='',
                routing_key=settings.RESULTS_QUEUE,
                body=result_msg.model_dump_json()
            )
        else:
            chunks_left = redis_client.decr(f"pending_chunks:{task.hash_value}")
            logger.debug(f"[Minion {settings.MINION_ID}] Chunks left for {task.hash_value}: {chunks_left}")
            if chunks_left == 0:
                status = redis_client.get(f"hash_status:{task.hash_value}")
                if status != "COMPLETED":
                    logger.info(
                        f"[Minion {settings.MINION_ID}] I'm the last chunk and no one found it! Hash is NOT_FOUND.")
                    result_msg = CrackResult(
                        hash_value=task.hash_value,
                        cracked_password=None,
                        minion_id=settings.MINION_ID,
                        not_found=True
                    )
                    ch.basic_publish(exchange='', routing_key=settings.RESULTS_QUEUE, body=result_msg.model_dump_json())

    except ValidationError as e:
        logger.error(f"[Minion {settings.MINION_ID}] Failed to validate task data: {e}", exc_info=True)
        raise e
    except Exception as e:
        logger.error(f"[Minion {settings.MINION_ID}] Unexpected error during message processing: {e}", exc_info=True)
        raise e
    finally:
        logger.info(f"[Minion {settings.MINION_ID}] Acknowledged message delivery_tag: {method.delivery_tag}")
        ch.basic_ack(delivery_tag=method.delivery_tag)


def start_worker():
    logger.info(f"Starting [Minion {settings.MINION_ID}] worker...")
    try:
        connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
        channel = connection.channel()

        channel.queue_declare(queue=settings.JOBS_QUEUE, durable=True)
        channel.queue_declare(queue=settings.RESULTS_QUEUE, durable=True)

        channel.basic_qos(prefetch_count=1)

        channel.basic_consume(
            queue=settings.JOBS_QUEUE,
            on_message_callback=process_message,
            auto_ack=False
        )
        logger.info(f"[Minion {settings.MINION_ID}] Connected to RabbitMQ. Waiting for jobs on '{settings.JOBS_QUEUE}'...")
        channel.start_consuming()
    except Exception as e:
        logger.error(f"[Minion {settings.MINION_ID}] Critical failure in worker loop: {e}", exc_info=True)