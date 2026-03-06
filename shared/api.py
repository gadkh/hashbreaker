from pydantic import BaseModel, Field
from typing import Optional
from shared.enums import TaskStatus

class CrackRequest(BaseModel):
    hash_value: str = Field(..., min_length=32, max_length=32, pattern=r"^[a-fA-F0-9]{32}$",
                            description="The MD5 hash to crack")

class CrackResponse(BaseModel):
    hash_value: str
    status: TaskStatus
    message: str
    password: Optional[str] = None

class StatusResponse(BaseModel):
    hash_value: str
    status: TaskStatus
    password: Optional[str] = None

class HealthResponse(BaseModel):
    status: str = Field(..., description="Current status of the service")
    service: str = Field(..., description="Name of the service responding")