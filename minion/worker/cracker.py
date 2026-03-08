import hashlib

def crack_chunk(target_hash: str, prefix: str, start_range: int, end_range: int): # -> str | None:
    for number in range(start_range, end_range + 1):
        phone_number = f"{prefix}-{number:07d}"
        calculated_hash = hashlib.md5(phone_number.encode('utf-8')).hexdigest()
        if calculated_hash == target_hash:
            return phone_number
    return None