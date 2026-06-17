from fastapi import APIRouter, HTTPException
from backend.schemas.mission import ActionPlanResponse
from backend.services.mission_service import get_action_plan

router = APIRouter()


@router.get('/action-plan/{plan_id}', response_model=ActionPlanResponse)
async def action_plan(plan_id: str):
    try:
        return await get_action_plan(plan_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc))
