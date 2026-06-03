# DESIGN.md: Architecture Overview

This document provides a high-level overview of the Store Intelligence Platform architecture, built to fulfill the end-to-end engineering challenge requirements.

## System Architecture

The platform is designed as a decoupled, real-time event processing system. It consists of three primary layers:

### 1. The Detection Layer (Edge)
The `detect.py` script acts as the "edge" compute node. It ingests raw video footage from the local file system. 
*   **Detection:** Uses YOLOv8 to locate human bounding boxes.
*   **Tracking:** Uses ByteTrack to assign consistent IDs across frames.
*   **Spatial Math:** Uses `shapely.geometry` to check if a tracking centroid intersects with predefined store zones mapped from `store_layout.json`.
*   **Emission:** Converts these intersections into normalized JSON events and pushes them to the Intelligence API via HTTP POST.

### 2. Cross-Camera Re-ID & Deduplication
To solve the critical issue of double-counting visitors across multiple camera feeds (e.g., from the entry door to the aisle), the tracker employs a **Visual Feature Re-ID mechanism**. 
*   Instead of blindly assigning new IDs to every detection, the `TrackerWrapper` extracts a visual feature embedding (128d) for each bounding box.
*   When a person leaves the frame and re-enters on another camera, their embedding is matched via Cosine Similarity (`> 0.85` threshold) against the feature cache. 
*   If matched, the pipeline assigns the original `visitor_id` and flags the event as a `REENTRY`, preventing inflated conversion rate denominators.

### 3. The Intelligence API (Core)
A containerized **FastAPI** application backed by **PostgreSQL**.
*   **Ingestion:** The `/events/ingest` endpoint handles incoming streams, utilizing SQL unique constraints on `event_id` to guarantee idempotency.
*   **Real-time Analytics:** Endpoints like `/metrics` and `/funnel` execute aggregate SQL queries to derive business value (conversion rates, queue depth) from raw events on the fly, eliminating the need for complex pre-calculated materialized views for the scale of this challenge.
*   **Anomaly Engine:** The `/anomalies` endpoint runs business-logic checks (e.g., "Is the queue depth suddenly > 5?", "Has no one entered the store in 30 minutes?") and flags them.
*   **POS Queue Abandonment:** The logic tracks `BILLING_QUEUE_JOIN`. If a visitor dwells in the billing zone for less than 15 seconds or never registers a matching transaction in the POS database within a 5-minute rolling window, the engine infers abandonment and triggers `BILLING_QUEUE_ABANDON`.

### 3. The Presentation Layer (Dashboard)
A modern, Apple-inspired **React + Vite** frontend.
*   Fetches data continuously on a 5-second polling interval.
*   Presents complex data in easily digestible visual components (Occupancy Area Charts, Zone Heatmaps).

## AI-Assisted Decisions

This platform was built using an "open-book" AI engineering philosophy. LLMs (specifically Google DeepMind models) were heavily utilized as pair-programmers and architectural sounding boards.

**1. Managing Database Schema Design:**
*   *Interaction:* I prompted the AI to help design an SQL schema that could answer both "What is the live queue depth?" and "What is the 7-day average conversion rate?".
*   *Decision:* The AI suggested a highly normalized `events` table with a `JSONB` metadata column. I completely agreed with this approach. It allows us to rigidly structure the core requirements (`timestamp`, `visitor_id`, `event_type`) while retaining the flexibility to inject unpredictable data (like `queue_depth` or `sku_zone`) into the `metadata_json` column without running database migrations.

**2. Frontend Polling vs. WebSockets:**
*   *Interaction:* I initially planned to implement WebSockets for the live dashboard to ensure 0-latency updates from the detection script. I asked the AI to generate the FastAPI WebSocket manager.
*   *Decision:* The AI correctly pointed out that maintaining persistent WebSocket connections for a dashboard that only requires visual updates every 5 seconds is unnecessary overhead and complicates container load balancing. I *overrode my initial choice* and followed the AI's advice to implement a standard 5-second `setInterval` HTTP polling mechanism in React.

**3. Test Coverage Strategy:**
*   *Interaction:* Writing boilerplate assertions for FastAPI endpoints is time-consuming. I provided the AI with my `schemas.py` and asked it to generate exhaustive edge-case tests (zero-purchases, empty clips). 
*   *Decision:* The AI generated `test_pipeline.py`. I accepted the core logic but *manually overrode* the mock database injection to ensure it correctly mocked the SQLAlchemy session lifecycle, which the AI initially hallucinated. The specific prompts used are documented in the headers of the test files.
