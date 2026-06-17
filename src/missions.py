from fastapi import APIRouter, HTTPException
from backend.schemas.mission import MissionResponse
from typing import List
from backend.services.mission_service import list_missions

router = APIRouter()


@router.get('/', response_model=List[MissionResponse])
async def get_missions():
    try:
        missions = await list_missions()
        return missions
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
