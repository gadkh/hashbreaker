from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from shared.api import CrackRequest, CrackResponse, StatusResponse
from master.db.database import get_session
from master.services import crack_service

router = APIRouter(prefix="/cracker", tags=["Cracker"])


@router.post("/crack", response_model=CrackResponse, status_code=status.HTTP_201_CREATED)
async def submit_hash(request: CrackRequest, db: AsyncSession = Depends(get_session)):
    return await crack_service.process_crack_request(request, db)


@router.get("/status/{hash_value}", response_model=StatusResponse, status_code=status.HTTP_200_OK)
async def get_status(hash_value: str, db: AsyncSession = Depends(get_session)):
    result = await crack_service.get_task_status(hash_value, db)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hash not found"
        )

    return result