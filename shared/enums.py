from enum import Enum

class TaskStatus(str, Enum):
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    NOT_FOUND = "NOT_FOUND"
    PENDING = "PENDING"