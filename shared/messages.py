from pydantic import BaseModel, Field

class ChunkTask(BaseModel):
    hash_value: str
    prefix: str = Field(..., description="Phone prefix, e.g., '050'")
    start_range: int = Field(..., description="Start of the 7-digit range")
    end_range: int = Field(..., description="End of the 7-digit range")

class CrackResult(BaseModel):
    hash_value: str
    cracked_password: str = Field(..., description="The found password, e.g., '050-1234567'")
    minion_id: str = Field(..., description="Identifier of the minion that solved it")