from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from app.models import get_db, Event, EventIngestRequest, BatchEventIngestRequest

logger = logging.getLogger(__name__)
router = APIRouter()

def process_single_event(event_req: EventIngestRequest, db: Session):
    existing = db.query(Event).filter(Event.event_id == event_req.event_id).first()
    if existing:
        return {"event_id": event_req.event_id, "status": "skipped", "reason": "Idempotent"}
        
    try:
        new_event = Event(
            event_id=event_req.event_id,
            store_id=event_req.store_id,
            camera_id=event_req.camera_id,
            event_type=event_req.event_type,
            timestamp=event_req.timestamp,
            visitor_id=event_req.visitor_id,
            track_id=event_req.track_id,
            zone_id=event_req.zone_id,
            dwell_ms=event_req.dwell_ms,
            is_staff=event_req.is_staff,
            embedding=event_req.embedding,
            metadata_json=event_req.metadata_json
        )
        db.add(new_event)
        db.commit()
        return {"event_id": event_req.event_id, "status": "success"}
    except IntegrityError as e:
        db.rollback()
        return {"event_id": event_req.event_id, "status": "error", "reason": "Database integrity error"}
    except Exception as e:
        db.rollback()
        return {"event_id": event_req.event_id, "status": "error", "reason": str(e)}

@router.post("/events/ingest", status_code=status.HTTP_201_CREATED)
def ingest_event(event_req: EventIngestRequest, db: Session = Depends(get_db)):
    """Single event ingestion."""
    result = process_single_event(event_req, db)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result)
    return result

@router.post("/events/ingest/batch", status_code=status.HTTP_207_MULTI_STATUS)
def ingest_event_batch(batch_req: BatchEventIngestRequest, db: Session = Depends(get_db)):
    """Batch event ingestion with partial success handling. Max 500 events."""
    if len(batch_req.events) > 500:
        raise HTTPException(status_code=400, detail="Batch size exceeds maximum of 500 events")
        
    results = []
    for event_req in batch_req.events:
        results.append(process_single_event(event_req, db))
        
    # Return 207 Multi-Status per REST conventions for partial success
    return {"status": "batch_processed", "results": results}
