from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class EventSchema(BaseModel):
    event_type: str
    timestamp: datetime
    track_id: str
    zone_id: Optional[str] = None
    embedding: Optional[List[float]] = None
    metadata_json: Optional[Dict[str, Any]] = None
