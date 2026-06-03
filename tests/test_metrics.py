# PROMPT: "Write a pytest suite for the metrics API endpoints in the Store Intelligence FastAPI application. Include tests for: GET /stores/{id}/metrics testing zero traffic handling, and GET /stores/{id}/funnel testing the conversion logic. Use fastapi.testclient."
# CHANGES MADE: Extracted these metrics tests from the monolithic test_pipeline.py into their own dedicated file for better modularity, and updated imports to match the new app/ structure.

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
import uuid

from app.main import app
from app.models import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_metrics.db"
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

def test_metrics_empty_store():
    # Store with no events should return 0s, not 500 error
    response = client.get("/stores/STORE_EMPTY_001/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["unique_visitors"] == 0
    assert data["current_occupancy"] == 0

def test_funnel_empty_store():
    # Funnel with no events should return 0s
    response = client.get("/stores/STORE_EMPTY_001/funnel")
    assert response.status_code == 200
    data = response.json()
    assert data["entry_count"] == 0
    assert data["queue_join_count"] == 0
