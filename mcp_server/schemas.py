from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    tool: str
    location: str
    status: str = "success"
    payload: Dict[str, Any] = Field(default_factory=dict)


class ResourceItem(BaseModel):
    name: str
    type: str
    status: str
    distance_km: float | None = None
    capacity: int | None = None


class ShelterCapacity(BaseModel):
    location: str
    shelters: List[Dict[str, Any]]
    total_capacity: int
    available_spaces: int


class WeatherAlert(BaseModel):
    location: str
    risk: str
    condition: str
    rainfall_mm: float
    wind_speed_kmph: float


class Allocation(BaseModel):
    location: str
    resources: List[ResourceItem]
    food: List[str] = Field(default_factory=list)
