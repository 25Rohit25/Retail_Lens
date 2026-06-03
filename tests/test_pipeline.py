# PROMPT: "Write a pytest suite for the Store Intelligence FastAPI application. Include tests for: POST /events/ingest ensuring idempotency, GET /health ensuring STALE_FEED works, and GET /stores/{id}/metrics handling an empty store gracefully. Use fastapi.testclient."
# CHANGES MADE: I modified the generated code to properly mock the SQLAlchemy database session dependency (`get_db`) using an in-memory SQLite database, because the AI initially tried to mock the DB inside the route itself, which didn't work.

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
import uuid

from app.main import app
from app.models import Base, get_db, Event

# Setup in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_health_check_empty_db():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["stale_feed"] == True

def test_ingest_event_idempotency():
    event_id = str(uuid.uuid4())
    payload = {
        "event_id": event_id,
        "store_id": "STORE_TEST_001",
        "camera_id": "CAM_01",
        "visitor_id": "VIS_01",
        "event_type": "ENTRY",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "zone_id": None,
        "dwell_ms": None,
        "is_staff": False,
        "confidence": 0.99,
        "metadata_json": {}
    }
    
    # First insert
    res1 = client.post("/events/ingest", json=payload)
    assert res1.status_code == 201
    
    # Second insert (should be idempotent)
    res2 = client.post("/events/ingest", json=payload)
    assert res2.status_code == 201
    assert "Idempotent" in res2.json()["message"]

def test_metrics_empty_store():
    # Store with no events should return 0s, not 500 error
    response = client.get("/stores/STORE_EMPTY_001/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["unique_visitors"] == 0
    assert data["current_occupancy"] == 0

def test_reentry_deduplication():
    # Simulate a visitor entering, exiting, and re-entering
    common_payload = {
        "store_id": "STORE_REENTRY_TEST",
        "camera_id": "CAM_01",
        "visitor_id": "VIS_01_BOB",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "zone_id": None, "dwell_ms": None, "is_staff": False, "confidence": 0.99, "metadata_json": {}
    }
    
    # 1. First Entry
    p1 = common_payload.copy()
    p1["event_id"] = str(uuid.uuid4())
    p1["event_type"] = "ENTRY"
    client.post("/events/ingest", json=p1)
    
    # 2. Re-entry (same visitor ID, new event ID)
    p2 = common_payload.copy()
    p2["event_id"] = str(uuid.uuid4())
    p2["event_type"] = "REENTRY"
    client.post("/events/ingest", json=p2)
    
    # Verify Metrics: Should only be 1 unique visitor, not 2
    response = client.get("/stores/STORE_REENTRY_TEST/metrics")
    assert response.json()["unique_visitors"] == 1

def test_group_entry():
    # 3 simultaneous bounding boxes should equal 3 separate ENTRY events
    for i in range(3):
        payload = {
            "event_id": str(uuid.uuid4()),
            "store_id": "STORE_GROUP_TEST",
            "camera_id": "CAM_01",
            "visitor_id": f"VIS_GROUP_{i}",
            "event_type": "ENTRY",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "zone_id": None, "dwell_ms": None, "is_staff": False, "confidence": 0.99, "metadata_json": {}
        }
        client.post("/events/ingest", json=payload)
        
    response = client.get("/stores/STORE_GROUP_TEST/metrics")
    assert response.json()["unique_visitors"] == 3

def test_batch_ingest():
    payload = {
        "events": [
            {
                "event_id": str(uuid.uuid4()),
                "store_id": "STORE_BATCH_001",
                "camera_id": "CAM_01",
                "visitor_id": "VIS_BATCH_1",
                "event_type": "ENTRY",
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "zone_id": None, "dwell_ms": None, "is_staff": False, "confidence": 0.99, "metadata_json": {}
            },
            {
                "event_id": str(uuid.uuid4()),
                "store_id": "STORE_BATCH_001",
                "camera_id": "CAM_01",
                "visitor_id": "VIS_BATCH_2",
                "event_type": "ENTRY",
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "zone_id": None, "dwell_ms": None, "is_staff": False, "confidence": 0.99, "metadata_json": {}
            }
        ]
    }
    
    response = client.post("/events/ingest/batch", json=payload)
    assert response.status_code == 207
    data = response.json()
    assert data["status"] == "batch_processed"
    assert len(data["results"]) == 2
    assert data["results"][0]["status"] == "success"
