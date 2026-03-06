from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from shared.api import CrackRequest, CrackResponse, StatusResponse
from master.db.database import get_session
from master.services import crack_service

router = APIRouter(prefix="cracker", tags=["Cracker"])


@router.post("/crack", response_model=CrackResponse, status_code=status.HTTP_201_CREATED)
def submit_hash(request: CrackRequest, db: Session = Depends(get_session)):
    return crack_service.process_crack_request(request, db)


@router.get("/status/{hash_value}", response_model=StatusResponse, status_code=status.HTTP_200_OK)
def get_status(hash_value: str, db: Session = Depends(get_session)):
    result = crack_service.get_task_status(hash_value, db)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hash not found"
        )

    return result