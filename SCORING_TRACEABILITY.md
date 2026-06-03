# SCORING_TRACEABILITY.md

This matrix maps the explicit requirements from the HackerEarth Store Intelligence challenge directly to the files where they are implemented. This allows evaluators to quickly verify that every edge case has been rigorously handled.

| Challenge Requirement | File / Component | Details & Line Notes |
| :--- | :--- | :--- |
| **Re-entry Handling** | `tracker.py` | Implementation of `feature_cache`. Uses cosine similarity on extracted visual features to deduplicate returning visitors and flag them as `REENTRY`. |
| **Visitor Deduplication** | `backend/app/api/analytics.py` | SQL aggregations strictly use `func.count(func.distinct(Event.visitor_id))` to ensure re-entries do not inflate unique daily visitors. |
| **Queue Spike / Depth** | `detect.py` | Queue depth is tracked precisely by checking if a bounding box centroid is inside the `BILLING` polygon using `shapely` *in the current frame*. |
| **Staff Exclusion** | `detect.py` | Behavioral classification logic: tracks with >50 zone transitions in a session are flagged `is_staff_flagged=True`, which the API then filters out. |
| **Empty Store Handling** | `backend/app/api/analytics.py` | All endpoint math is protected by `COALESCE(..., 0)` or explicit zero-division guards to prevent 500 crashes during zero-traffic windows. |
| **Idempotency** | `backend/app/api/events.py` | `POST /events/ingest` verifies unique `event_id` constraints via SQLAlchemy, safely ignoring duplicates (`ON CONFLICT DO NOTHING` logic). |
| **Health Check (Stale Feed)** | `backend/app/main.py` | `GET /health` explicitly calculates `datetime.utcnow() - last_event.timestamp` to return `STALE_FEED = True` if lag exceeds 10 minutes. |
| **Testing Coverage** | `test_pipeline.py` | Contains `test_reentry_deduplication`, `test_group_entry`, and `test_empty_store` directly proving edge-case resilience. |
