from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Any, Optional


class MongoRecord(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={datetime: lambda value: value.isoformat()},
    )

    id: Optional[str] = Field(None, alias='_id')
    created_at: Optional[datetime] = Field(None, alias='createdAt')


class GeoPoint(BaseModel):
    latitude: float
    longitude: float


class AllocationItem(BaseModel):
    item: str
    quantity: int
    assigned_to: str
    notes: Optional[str] = None

class ShelterCapcity(BaseModel):
    shelter: str
    capacity: int
    occupied: int

class ResourceSummary(BaseModel):
    resource: str
    quantity: int
    allocated: int
    available: int

class ResourceAllocation(BaseModel):
    houses_vacated: int 
    ambulances_dispatched: int 
    medical_team_deployment: int 
    food_packs: int
    water_crates: int
    shelters_activated: int
    heavy_rescue_teams: int
    
