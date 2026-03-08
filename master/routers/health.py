from fastapi import APIRouter, status

from shared.api import HealthResponse

router = APIRouter(prefix="/health", tags=["System Health"])

@router.get("/", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health():
    return HealthResponse(status="OK", service="master-api")
