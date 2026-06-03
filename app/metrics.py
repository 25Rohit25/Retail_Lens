from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import get_db, Event

router = APIRouter()

@router.get("/stores/{store_id}/metrics")
def get_metrics(store_id: str, db: Session = Depends(get_db)):
    """Returns top-level KPIs for the dashboard."""
    unique_visitors = db.query(func.count(func.distinct(Event.visitor_id))).filter(
        Event.store_id == store_id, 
        Event.is_staff == False
    ).scalar() or 0
    
    entries_count = db.query(func.count(func.distinct(Event.visitor_id))).filter(
        Event.store_id == store_id,
        Event.event_type == "ENTRY",
        Event.is_staff == False
    ).scalar() or 0
    
    exits_count = db.query(func.count(func.distinct(Event.visitor_id))).filter(
        Event.store_id == store_id,
        Event.event_type == "EXIT",
        Event.is_staff == False
    ).scalar() or 0
    
    current_occupancy = max(0, entries_count - exits_count)
    
    avg_dwell = db.query(func.avg(Event.dwell_ms)).filter(
        Event.store_id == store_id,
        Event.dwell_ms.isnot(None)
    ).scalar()
    avg_dwell_val = float(avg_dwell) if avg_dwell is not None else 0.0
    
    staff_count = db.query(func.count(func.distinct(Event.visitor_id))).filter(
        Event.store_id == store_id,
        Event.is_staff == True
    ).scalar() or 0

    return {
        "store_id": store_id, 
        "unique_visitors": unique_visitors,
        "current_occupancy": current_occupancy, 
        "avg_dwell_time_seconds": avg_dwell_val / 1000.0, 
        "staff_count": staff_count
    }
