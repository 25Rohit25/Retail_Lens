from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import get_db, Event, Session as VisitorSession, FunnelResponse

router = APIRouter()

@router.get("/stores/{store_id}/funnel", response_model=FunnelResponse)
def get_funnel(store_id: str, db: Session = Depends(get_db)):
    """Calculates the end-to-end conversion funnel."""
    entries = db.query(func.count(func.distinct(Event.visitor_id))).filter(
        Event.store_id == store_id, Event.event_type == "ENTRY", Event.is_staff == False
    ).scalar() or 0
    
    zones = db.query(func.count(func.distinct(Event.visitor_id))).filter(
        Event.store_id == store_id, 
        Event.event_type == "ZONE_DWELL",
        Event.dwell_ms > 10000,
        Event.is_staff == False
    ).scalar() or 0
    
    queues = db.query(func.count(func.distinct(Event.visitor_id))).filter(
        Event.store_id == store_id, Event.event_type == "BILLING_QUEUE_JOIN", Event.is_staff == False
    ).scalar() or 0
    
    abandons = db.query(func.count(func.distinct(Event.visitor_id))).filter(
        Event.store_id == store_id, Event.event_type == "BILLING_QUEUE_ABANDON", Event.is_staff == False
    ).scalar() or 0
    
    # Since we don't have POS logs for the hackathon, we infer purchases 
    # as anyone who joined the queue and did NOT abandon it.
    purchases = max(0, queues - abandons)
    
    return FunnelResponse(
        entry_count=entries,
        zone_count=zones,
        queue_join_count=queues,
        purchase_count=purchases,
        queue_abandonment_count=abandons,
    )
