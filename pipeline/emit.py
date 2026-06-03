import requests
import uuid
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("emit")

API_URL = "http://localhost:8000/events/ingest"

def emit_event(store_id, camera_id, visitor_id, event_type, timestamp, zone_id=None, dwell_ms=None, is_staff=False, confidence=1.0, metadata=None):
    """
    Formats and emits an event matching the exact Required Output Schema from the challenge.
    """
    event_payload = {
        "event_id": str(uuid.uuid4()),
        "store_id": store_id,
        "camera_id": camera_id,
        "visitor_id": str(visitor_id),
        "event_type": event_type,
        "timestamp": timestamp,
        "zone_id": zone_id,
        "dwell_ms": dwell_ms,
        "is_staff": is_staff,
        "confidence": float(confidence),
        "metadata": metadata or {}
    }
    
    try:
        response = requests.post(API_URL, json=event_payload, timeout=2)
        if response.status_code == 201:
            logger.info(f"Emitted: {event_type} for {visitor_id} at {zone_id or 'STORE'}")
        else:
            logger.error(f"Failed to emit: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Connection error when emitting event: {e}")
