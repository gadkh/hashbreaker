from shared.messages import ChunkTask
from master.services.queue_pub import publish_tasks
from shared.logger import setup_logger

logger = setup_logger(__name__)

PREFIXES = ["050", "051", "052", "053", "054", "055", "058", "059"]

CHUNK_SIZE = 1_000_000

async def dispatch_crack_task(hash_value: str):
    logger.info(f"Starting to split job for hash {hash_value} into chunks...")
    tasks_to_publish = []
    for prefix in PREFIXES:
        for start in range(0, 10_000_000, CHUNK_SIZE):
            end = start + CHUNK_SIZE - 1

            if end > 9_999_999:
                end = 9_999_999

            task = ChunkTask(
                hash_value=hash_value,
                prefix=prefix,
                start_range=start,
                end_range=end
            )
            tasks_to_publish.append(task)
    logger.info(f"Prepared {len(tasks_to_publish)} chunks. Sending to RabbitMQ...")
    await publish_tasks(tasks_to_publish)
    logger.info(f"Successfully dispatched all {len(tasks_to_publish)} chunks to the queue for hash {hash_value}")
