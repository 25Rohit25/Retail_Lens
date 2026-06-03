from typing import List, Dict, Any
from ultralytics import YOLO

class ByteTracker:
    def __init__(self, tracker_config: str = "bytetrack.yaml"):
        """
        Initializes ByteTrack. 
        Note: We are wrapping Ultralytics' integrated tracking system for simplicity and performance.
        It uses the same YOLO model but calls .track() instead.
        """
        self.tracker_config = tracker_config
        # We hold a reference to the tracker state. 
        # For full control, we use YOLO.track, which handles ByteTrack natively.
        
    def update(self, model: YOLO, frame, conf_thresh: float = 0.5, classes: list = [0]) -> List[Dict[str, Any]]:
        """
        Runs ByteTrack on the current frame.
        Returns active tracks.
        """
        results = model.track(frame, persist=True, tracker=self.tracker_config, conf=conf_thresh, classes=classes, verbose=False)
        
        active_tracks = []
        if len(results) > 0 and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.int().cpu().numpy()
            
            for box, track_id in zip(boxes, track_ids):
                active_tracks.append({
                    "track_id": str(track_id),
                    "bbox": box.tolist() # [x1, y1, x2, y2]
                })
                
        return active_tracks
