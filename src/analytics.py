from fastapi import APIRouter, HTTPException
from backend.schemas.analytics import AnalyticsResponse
from backend.services.analytics_service import fetch_analytics

router = APIRouter()


@router.get('/analytics', response_model=AnalyticsResponse)
async def analytics():
    try:
        return await fetch_analytics()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
