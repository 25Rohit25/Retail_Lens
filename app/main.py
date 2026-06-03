from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
import uuid
import logging
import json

from app.models import engine, Base
from app import ingestion, metrics, funnel, anomalies, health

# 1. Initialize Application Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("fastapi_app")

# 2. Database Initialization
Base.metadata.create_all(bind=engine)

# 3. FastAPI Initialization
app = FastAPI(
    title="Store Intelligence Platform API", 
    version="1.0.0",
    description="Backend API for processing CV events and serving analytics dashboards."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Structured Logging Middleware (Required by challenge rubric)
@app.middleware("http")
async def structured_logging_middleware(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-Id", str(uuid.uuid4()))
    start_time = time.time()
    
    response = await call_next(request)
    
    latency_ms = (time.time() - start_time) * 1000.0
    
    # Generate structured log
    log_data = {
        "trace_id": trace_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "latency_ms": round(latency_ms, 2)
    }
    
    logger.info(json.dumps(log_data))
    
    response.headers["X-Trace-Id"] = trace_id
    return response

# 4. Include Routers
app.include_router(ingestion.router, tags=["ingestion"])
app.include_router(metrics.router, tags=["analytics"])
app.include_router(funnel.router, tags=["analytics"])
app.include_router(anomalies.router, tags=["analytics"])
app.include_router(health.router, tags=["monitoring"])
