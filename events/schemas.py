from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime
import uuid

# Define literal for supported event types to enable strict validation
EventType = Literal[
    "ENTRY",
    "EXIT",
    "ZONE_ENTER",
    "ZONE_EXIT",
    "ZONE_DWELL",
    "BILLING_QUEUE_JOIN",
    "BILLING_QUEUE_ABANDON",
    "REENTRY"
]

class Event(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    visitor_id: str
    track_id: Optional[str] = None
    zone_id: Optional[str] = None
    dwell_time_seconds: Optional[float] = None
    embedding: Optional[List[float]] = None
    metadata_json: Optional[Dict[str, Any]] = None

    @field_validator("dwell_time_seconds")
    @classmethod
    def validate_dwell_time(cls, v, info):
        # Strict validation: DWELL events MUST have a dwell time.
        if info.data.get("event_type") == "ZONE_DWELL" and v is None:
            raise ValueError("dwell_time_seconds is required for ZONE_DWELL events")
        if v is not None and v < 0:
            raise ValueError("dwell_time_seconds cannot be negative")
        return v
        
    @field_validator("zone_id")
    @classmethod
    def validate_zone_id(cls, v, info):
        # Strict validation: Zone-related events MUST have a zone_id.
        event_type = info.data.get("event_type")
        zone_events = ["ZONE_ENTER", "ZONE_EXIT", "ZONE_DWELL", "BILLING_QUEUE_JOIN", "BILLING_QUEUE_ABANDON"]
        if event_type in zone_events and v is None:
            raise ValueError(f"zone_id is required for {event_type} events")
        return v
