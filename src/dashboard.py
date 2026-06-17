from fastapi import APIRouter, HTTPException
from backend.schemas.analytics import DashboardStats
from backend.services.analytics_service import fetch_dashboard_stats

router = APIRouter()


@router.get('/dashboard', response_model=DashboardStats)
async def dashboard():
    try:
        return await fetch_dashboard_stats()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
