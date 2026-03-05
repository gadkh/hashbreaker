from sqlalchemy import Column, String, Enum, DateTime
from sqlalchemy.sql import func
import enum
from ..database import Base

class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    EXHAUSTED = "EXHAUSTED"

class HashTask(Base):
    __tablename__ = "hash_tasks"
    hash_value = Column(String(32), primary_key=True, index=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    cracked_password = Column(String(11), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())