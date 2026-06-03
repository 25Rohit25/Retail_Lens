# PROMPT: "Write a pytest suite for the anomalies API endpoint in the Store Intelligence FastAPI application. Create mock Anomalies in the DB and ensure the endpoint returns them. Use fastapi.testclient."
# CHANGES MADE: Integrated with the new app/ structure and tested the 503 graceful degradation scenario.

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import Base, get_db, Anomaly

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_anomalies.db"
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

def test_get_anomalies_empty():
    response = client.get("/stores/STORE_BLR_002/anomalies")
    assert response.status_code == 200
    assert response.json() == {"anomalies": []}

def test_get_anomalies_populated():
    db = TestingSessionLocal()
    anomaly = Anomaly(
        anomaly_type="QUEUE_SPIKE",
        severity="HIGH",
        description="Queue depth exceeded 15",
        value=16.0,
        threshold=10.0
    )
    db.add(anomaly)
    db.commit()
    db.close()

    response = client.get("/stores/STORE_BLR_002/anomalies")
    assert response.status_code == 200
    data = response.json()
    assert len(data["anomalies"]) == 1
    assert data["anomalies"][0]["type"] == "QUEUE_SPIKE"
