import requests
import uuid
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("emit")

API_URL = "http://localhost:8000/events/ingest/batch"
EVENT_BUFFER = []
BATCH_SIZE = 50

def flush_events():
    global EVENT_BUFFER
    if not EVENT_BUFFER:
        return
        
    try:
        response = requests.post(API_URL, json={"events": EVENT_BUFFER}, timeout=10)
        if response.status_code in [200, 201, 207]:
            logger.info(f"Successfully batch emitted {len(EVENT_BUFFER)} events.")
        else:
            logger.error(f"Failed to emit batch: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Connection error when emitting batch: {e}")
    finally:
        EVENT_BUFFER.clear()

def emit_event(store_id, camera_id, visitor_id, event_type, timestamp, zone_id=None, dwell_ms=None, is_staff=False, confidence=1.0, metadata=None):
    """
    Formats and emits an event matching the exact Required Output Schema from the challenge.
    """
    global EVENT_BUFFER
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
    
    EVENT_BUFFER.append(event_payload)
    
    if len(EVENT_BUFFER) >= BATCH_SIZE:
        flush_events()
