from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional, Any
from datetime import datetime
from backend.schemas.common import GeoPoint, MongoRecord


class AlertCreateRequest(BaseModel):
    disaster_type: str
    location: str
    impact_window: str
    description: str
    estimated_population: int
    area_geo: Optional[GeoPoint] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Extra context for MCP/A2A")


class AlertResponse(MongoRecord):
    """Schema for Alert data, compatible with LangGraph State and MCP brokers."""
    alert_id: str
    disaster_type: str
    status: str = Field(default="Awaiting Mission", description="Current state in the LangGraph workflow")
    risk_score: int = 0
    vulnerable_zones: List[str] = Field(default_factory=list)
    estimated_population: int = 0
    
    # LangGraph/MCP State fields
    external_data: Dict[str, Any] = Field(default_factory=dict, description="Data fetched from Weather/IMD/Healthcare tools")
    analysis_summary: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)
