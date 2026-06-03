import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from pydantic import BaseModel

# --- DATABASE SETUP ---
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/store_intelligence")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- SQLALCHEMY MODELS ---
class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True) 
    store_id = Column(String, index=True)
    camera_id = Column(String, nullable=True)
    event_type = Column(String, index=True) 
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    track_id = Column(String, index=True)
    visitor_id = Column(String, index=True, nullable=True) 
    zone_id = Column(String, nullable=True)
    dwell_ms = Column(Integer, nullable=True)
    is_staff = Column(Boolean, default=False)
    embedding = Column(JSON, nullable=True) 
    metadata_json = Column(JSON, nullable=True) 

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String, index=True)
    visitor_id = Column(String, unique=True, index=True)
    first_seen = Column(DateTime, index=True)
    last_seen = Column(DateTime, index=True)
    is_converted = Column(Boolean, default=False)
    is_staff = Column(Boolean, default=False)
    total_dwell_time = Column(Float, default=0.0) 

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String, index=True)
    transaction_id = Column(String, unique=True, index=True)
    timestamp = Column(DateTime, index=True)
    basket_value_inr = Column(Float)
    matched_visitor_id = Column(String, ForeignKey("sessions.visitor_id"), nullable=True)

class Anomaly(Base):
    __tablename__ = "anomalies"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    anomaly_type = Column(String, index=True) 
    severity = Column(String) 
    description = Column(String)
    value = Column(Float)
    threshold = Column(Float)

# --- PYDANTIC SCHEMAS ---
class EventIngestRequest(BaseModel):
    event_id: str
    store_id: str
    camera_id: Optional[str] = None
    event_type: str
    timestamp: datetime
    visitor_id: str
    track_id: Optional[str] = None
    zone_id: Optional[str] = None
    dwell_ms: Optional[int] = None
    is_staff: Optional[bool] = False
    embedding: Optional[List[float]] = None
    metadata_json: Optional[Dict[str, Any]] = None

class BatchEventIngestRequest(BaseModel):
    events: List[EventIngestRequest]

class HealthResponse(BaseModel):
    status: str
    last_event_timestamp: Optional[datetime]
    stale_feed: bool

class FunnelResponse(BaseModel):
    entry_count: int
    zone_count: int
    queue_join_count: int
    purchase_count: int
    queue_abandonment_count: int
