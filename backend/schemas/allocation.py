from fastapi import APIRouter, HTTPException
from backend.schemas.alert import AlertCreateRequest, AlertResponse
from backend.services.agent_runner import dispatch_disaster_alert

router = APIRouter()


@router.post('/', response_model=AlertResponse)
async def create_alert(alert_request: AlertCreateRequest):
    try:
        result = await dispatch_disaster_alert(alert_request)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
