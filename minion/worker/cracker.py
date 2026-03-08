import hashlib
from typing import Optional
from minion.core.config import settings
from shared.enums import TaskStatus
import redis

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

def check_in_redis(target_hash: str) -> bool:
    status = redis_client.get(f"hash_status:{target_hash}")
    return status == TaskStatus.COMPLETED.value

def crack_chunk(target_hash: str, prefix: str, start_range: int, end_range: int) -> Optional[str]:
    for index, number in enumerate(range(start_range, end_range + 1)):
        if index % 10_000 == 0:
            if check_in_redis(target_hash):
                return None
        phone_number = f"{prefix}-{number:07d}"
        calculated_hash = hashlib.md5(phone_number.encode('utf-8')).hexdigest()
        if calculated_hash == target_hash:
            return phone_number
    return None