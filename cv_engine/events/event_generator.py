import json
from datetime import datetime
from typing import Dict, List, Any
import cv2
import numpy as np
from .schemas import EventSchema

class EventGenerator:
    def __init__(self, output_file: str = "events.jsonl"):
        self.output_file = output_file
        self.active_tracks: Dict[str, Dict[str, Any]] = {}
        self.track_zones: Dict[str, str] = {}
        
    def _write_event(self, event: EventSchema):
        with open(self.output_file, 'a') as f:
            # Convert datetime to ISO string for JSON serialization
            data = event.model_dump()
            data['timestamp'] = data['timestamp'].isoformat()
            f.write(json.dumps(data) + '\n')

    def _is_point_in_polygon(self, point: tuple, polygon: List[List[float]]) -> bool:
        poly_arr = np.array(polygon, dtype=np.int32)
        # cv2.pointPolygonTest returns >0 if inside, 0 if on edge, <0 if outside
        return cv2.pointPolygonTest(poly_arr, point, False) >= 0

    def process_frame(self, current_tracks: List[Dict[str, Any]], embeddings: List[List[float]], timestamp: datetime, zones: List[Dict[str, Any]]):
        current_track_ids = set()
        
        for idx, track in enumerate(current_tracks):
            track_id = track['track_id']
            bbox = track['bbox']
            current_track_ids.add(track_id)
            embedding = embeddings[idx] if idx < len(embeddings) else None
            
            # 1. Check ENTRY
            if track_id not in self.active_tracks:
                self.active_tracks[track_id] = {'first_seen': timestamp, 'last_seen': timestamp}
                event = EventSchema(
                    event_type="ENTRY",
                    timestamp=timestamp,
                    track_id=track_id,
                    embedding=embedding,
                    metadata_json={"bbox": bbox}
                )
                self._write_event(event)
            else:
                self.active_tracks[track_id]['last_seen'] = timestamp
                
            # 2. Zone Logic
            # Calculate bottom-center of bbox
            x1, y1, x2, y2 = bbox
            bc_x = (x1 + x2) / 2
            bc_y = y2
            
            current_zone = None
            for zone in zones:
                if self._is_point_in_polygon((bc_x, bc_y), zone['polygon']):
                    current_zone = zone['zone_id']
                    break
                
            prev_zone = self.track_zones.get(track_id)
            
            if current_zone != prev_zone:
                if prev_zone is not None:
                    # Exited previous zone
                    self._write_event(EventSchema(
                        event_type="ZONE_EXIT", timestamp=timestamp, track_id=track_id, zone_id=prev_zone
                    ))
                if current_zone is not None:
                    # Entered new zone
                    event_type = "BILLING_QUEUE_JOIN" if "billing" in current_zone.lower() else "ZONE_ENTER"
                    self._write_event(EventSchema(
                        event_type=event_type, timestamp=timestamp, track_id=track_id, zone_id=current_zone
                    ))
                self.track_zones[track_id] = current_zone

        # 3. Check EXIT
        lost_tracks = set(self.active_tracks.keys()) - current_track_ids
        for track_id in lost_tracks:
            last_seen = self.active_tracks[track_id]['last_seen']
            # 5 seconds grace period before emitting EXIT
            if (timestamp - last_seen).total_seconds() > 5.0: 
                prev_zone = self.track_zones.get(track_id)
                if prev_zone:
                    self._write_event(EventSchema(
                        event_type="ZONE_EXIT", timestamp=timestamp, track_id=track_id, zone_id=prev_zone
                    ))
                    del self.track_zones[track_id]
                    
                self._write_event(EventSchema(
                    event_type="EXIT", timestamp=timestamp, track_id=track_id
                ))
                del self.active_tracks[track_id]
