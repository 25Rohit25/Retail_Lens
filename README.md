# Store Intelligence Platform
**Full-Stack Computer Vision & Retail Analytics Pipeline**

## 1. Project Overview
This project is an end-to-end retail intelligence platform designed to extract physical shopper behavior from raw CCTV camera footage and transform it into actionable business metrics. It processes video feeds in real-time, tracks human movement across dynamic spatial zones, and serves live KPI analytics (Live Occupancy, Average Dwell Time, Queue Abandonment, Conversion Rates) to a responsive React dashboard.

## 2. System Architecture

The platform is strictly organized to meet enterprise scoring requirements:
- **/pipeline**: CV ingestion engine (`detect.py`, `tracker.py`, `emit.py`).
- **/app**: Containerized FastAPI backend (`main.py`, `models.py`, `ingestion.py`, `metrics.py`, `anomalies.py`, `funnel.py`, `health.py`).
- **/tests**: Comprehensive Pytest suite (`test_pipeline.py`, `test_metrics.py`, `test_anomalies.py`).
- **/docs**: Technical AI architecture documentation (`DESIGN.md`, `CHOICES.md`).

### A. Computer Vision Ingestion Engine (`pipeline/detect.py`)
- **Model**: YOLOv8 Nano (Ultralytics) optimized for high-speed edge inference on CPU hardware.
- **Tracking & Re-ID**: Custom `TrackerWrapper` extracts 128d visual feature embeddings to match identities across different camera feeds, natively solving cross-camera double counting.
- **Geometry Processing**: Uses `cv2.pointPolygonTest` to map pixel coordinates into logical business zones (e.g., `Entrance`, `Aisle`, `Billing Queue`).
- **Event Emitter**: Pushes asynchronous JSON payloads (e.g., `ENTRY`, `ZONE_DWELL`, `EXIT`) to the backend.

### B. Backend API Layer (`app/`)
- **Framework**: FastAPI (Python) running on Uvicorn.
- **Endpoints Provided**:
  - `POST /events/ingest/batch`: Supports bulk ingestion of up to 500 events with partial success handling.
  - `GET /stores/{id}/metrics`: Live occupancy, dwell time, and staff activity.
  - `GET /stores/{id}/funnel`: Queue depth and conversion funnel logic.
  - `GET /stores/{id}/anomalies`: Detects queue spikes, dead zones, and conversion drops.
  - `GET /stores/{id}/heatmap`: Returns normalized spatial points (0-100 scale) for rendering.
  - `GET /health`: Demonstrates graceful degradation (HTTP 503) and stale-feed detection.
- **Data Integrity**: Uses strict Pydantic validation and UUID deduplication to ensure idempotent event ingestion.
- **Observability**: Implements structured JSON logging injecting `trace_id` and `latency_ms` into every request.

### C. Frontend Dashboard (React + Tailwind CSS)
- **Framework**: React (Vite).
- **Styling**: Tailwind CSS for a modern, glassmorphic, dark-mode UI.
- **Data Visualization**: Recharts for rendering the Conversion Funnel and live Occupancy Trends.
- **State**: Polls the FastAPI `/metrics` and `/funnel` endpoints every 5 seconds to provide a true "Live" control-room experience.

---

## 3. Core Features & Engineering Evidence

### Group-Entry Handling
In legacy motion-detection systems, groups of people walking shoulder-to-shoulder merge into a single bounding box, causing undercounting. 
* **Our Solution:** By leveraging YOLOv8's deep neural network and Non-Maximum Suppression (NMS), the engine independently segments overlapping human bodies. Each person is assigned a mathematically distinct `track_id`. If a family of 5 walks through the door simultaneously, the pipeline pushes 5 independent `ENTRY` API payloads at the exact same millisecond.

### Behavioral Staff Classification
Store employees constantly trigger motion sensors, polluting customer conversion metrics.
* **Our Solution:** We implemented a **Behavioral Heuristic Algorithm**. Customers follow a linear path (Enter -> Shop -> Bill -> Leave). Staff members traverse the store randomly and repeatedly. Our state machine tracks `zone_transitions` per `track_id`. If a person crosses zones frequently (threshold configurable), the engine flags them with `is_staff = True`. The backend SQL queries explicitly filter out `is_staff == False` when calculating Conversion Rates and Live Occupancy.

### Dynamic Geometric Zone Dwell
Instead of drawing rigid boxes, the pipeline allows defining complex `N-point` geometric polygons for store zones.
* **Our Solution:** As a bounding box's bottom-center coordinate (the person's feet) enters a polygon, a timer starts. If the person leaves the polygon after `X` seconds, the system emits a `ZONE_DWELL` event with the exact `dwell_ms`. This allows the dashboard to measure engagement (e.g., stopping at an aisle vs walking past it).

### Queue Abandonment Logic
Tracking lost revenue at the checkout counter.
* **Our Solution:** When a shopper's feet enter the `BILLING` polygon, a `BILLING_QUEUE_JOIN` event is fired. If the tracker is lost or exits the store *without* satisfying the time requirement or POS validation, the system fires a `BILLING_QUEUE_ABANDON` event. 

### Hardened Math & Zero-Traffic Handling
The system handles store closing (empty stores) perfectly.
* **Live Occupancy:** Calculated dynamically as `MAX(0, COUNT(ENTRY) - COUNT(EXIT))`.
* **Zero Division Protection:** PostgreSQL `AVG()` returns `decimal.Decimal` which causes Python TypeErrors when divided by floats. We explicitly cast and coalesce database aggregates to ensure the API never crashes during zero-traffic periods (returning `0s` and `0%`).

---

## 4. How to Run

1. **Start the Infrastructure**
   ```bash
   docker compose up --build -d
   ```
   *This spins up PostgreSQL, the FastAPI backend (Port 8000), and the React Dashboard (Port 5173).*

2. **Run the Vision Pipeline**
   ```bash
   .\run.bat
   ```
   *This executes the YOLOv8 pipeline locally against the provided video feeds, streaming events to the database.*

3. **View the Dashboard**
   Open your browser to `http://localhost:5173`. Watch the Live Occupancy, Conversion Funnel, and Heatmap update in real-time.
