from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from shared.api import CrackRequest, CrackResponse, StatusResponse
from shared.logger import setup_logger
from master.db.database import get_session
from master.services import crack_service

logger = setup_logger(__name__)

router = APIRouter(prefix="/cracker", tags=["Cracker"])


@router.post("/crack", response_model=CrackResponse, status_code=status.HTTP_201_CREATED)
async def submit_hash(request: CrackRequest, db: AsyncSession = Depends(get_session)):
    logger.info(f"Received POST /crack request for hash: {request.hash_value}")
    return await crack_service.process_crack_request(request, db)


@router.get("/status/{hash_value}", response_model=StatusResponse, status_code=status.HTTP_200_OK)
async def get_status(hash_value: str, db: AsyncSession = Depends(get_session)):
    logger.info(f"Get  /status for hash: {hash_value}")
    result = await crack_service.get_task_status(hash_value, db)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hash not found"
        )

    return result