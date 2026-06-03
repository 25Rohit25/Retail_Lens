# CHOICES.md

This document outlines the core architectural and engineering tradeoffs made during the development of the Store Intelligence Platform, fulfilling Part D of the hiring challenge requirements.

## 1. Detection Model Selection

**Goal:** Detect, track, and assign a unique token to individuals moving through a complex physical retail environment with occlusions and edge cases like staff movement and group entry.

**Options Considered:**
1. **YOLOv8 + ByteTrack (Chosen):** YOLOv8 is fast and highly accurate for human detection. ByteTrack associates bounding boxes robustly across frames using both IoU and visual feature cues, even under partial occlusion.
2. **MediaPipe Pose Tracking:** Excellent for precise skeleton tracking, but computationally expensive and struggles with dense crowds or extreme occlusions common in billing queues.
3. **RT-DETR + DeepSORT:** RT-DETR offers real-time transformer-based detection, but DeepSORT relies heavily on an outdated Re-ID network that struggles with varying camera lighting.

**AI Suggestion & Rationale:** 
During the initial planning phase, the AI suggested utilizing YOLOv8 coupled with DeepSORT. However, after further prompting to evaluate DeepSORT's performance on highly occluded "billing queue" scenarios, the AI correctly identified that ByteTrack's ability to retain low-confidence detection boxes (rather than eagerly discarding them) yields significantly fewer fragmented tracks in crowded retail scenarios. 

**What I Chose & Why:**
I chose **YOLOv8 Nano + ByteTrack**. While YOLOv8 Small or Medium provides higher raw mAP, the Nano variant allows the pipeline to run continuously at 30+ FPS on edge hardware without requiring dedicated enterprise GPUs. In retail environments (like the billing queue edge case), people stand close together and often occlude each other. ByteTrack mitigates the Nano model's occasional lower-confidence partial-occlusion misses by maintaining track momentum and identity persistence even when the detection box briefly drops below the confidence threshold.

## 2. Event Schema Design

**Goal:** Create a normalized, scalable JSON schema that the detection pipeline can emit, and the backend can ingest idempotently to power real-time analytics.

**Options Considered:**
1. **Raw Trajectory Stream (Every frame):** Emitting a coordinate `(x, y)` for every visitor in every frame. 
2. **State-Change Event Stream (Chosen):** Emitting discrete events (`ENTRY`, `ZONE_ENTER`, `ZONE_DWELL`, `EXIT`) only when a visitor crosses a logical threshold or completes a state.
3. **Session-Aggregated JSON:** Sending a single massive JSON blob when the visitor leaves the store containing their entire history.

**AI Suggestion & Rationale:**
The AI strongly advocated for the **State-Change Event Stream**, pointing out that streaming 15fps trajectory coordinates to a PostgreSQL database would require specialized time-series databases (like TimescaleDB) and completely overwhelm a standard relational database with noise, without adding business value.

**What I Chose & Why:**
I chose the **State-Change Event Stream** with strict idempotency (via a UUID `event_id`). 
*   **Scalability:** By shifting the computation of "has this person dwelled for 30 seconds" to the edge (the detection script), the API is shielded from high-frequency noise.
*   **Idempotency:** A unique `event_id` ensures that if the detection script restarts mid-video and re-processes a clip, the `POST /events/ingest` endpoint can use a simple SQL `ON CONFLICT DO NOTHING` to guarantee exact-once semantics.

## 3. API Architecture Choice

**Goal:** Build a production-ready, highly concurrent API that ingests events and computes analytics in real-time.

**Options Considered:**
1. **FastAPI + PostgreSQL (Chosen):** Asynchronous python web framework with standard relational mapping (SQLAlchemy).
2. **Node.js + MongoDB:** Fast I/O, schema-less document storage.
3. **Django + PostgreSQL:** Full-batteries-included monolithic framework.

**AI Suggestion & Rationale:**
I asked the AI to compare FastAPI and Node.js for this specific challenge. The AI recommended FastAPI, citing that the data science and computer vision ecosystem is overwhelmingly Python-native. If the API ever needs to load a VLM or run an anomaly detection machine learning model directly in the backend, remaining in the Python ecosystem is a massive advantage.

**What I Chose & Why:**
I chose **FastAPI with PostgreSQL**. 
*   The `async` capabilities of FastAPI allow it to handle thousands of concurrent `POST /events/ingest` requests seamlessly.
*   I chose PostgreSQL over a NoSQL database because the analytics queries (e.g., Conversion Funnel, Anomaly Detection against a 7-day average) require complex `GROUP BY` and window functions that are far more expressive and performant in standard SQL than in MongoDB aggregation pipelines.
