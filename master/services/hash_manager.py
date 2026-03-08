from shared.messages import ChunkTask
from master.services.queue_pub import publish_tasks

PREFIXES = ["050", "051", "052", "053", "054", "055", "058", "059"]

CHUNK_SIZE = 1_000_000

async def dispatch_crack_task(hash_value: str):
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

    await publish_tasks(tasks_to_publish)
