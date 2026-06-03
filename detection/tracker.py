from ultralytics import YOLO
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class Tracker:
    def __init__(self):
        """
        Initializes the ByteTrack tracker via Ultralytics native integration.
        """
        self.tracker_yaml = "bytetrack.yaml"
        logger.info("Initialized ByteTrack tracker configuration")

    def track(self, model: YOLO, frame, conf: float) -> List[Dict[str, Any]]:
        """
        Runs ByteTrack tracking.
        Args:
            model: Instantiated YOLO model.
            frame: Image frame (BGR).
            conf: Confidence threshold.
        Returns:
            List of dictionaries containing track_id, bbox, and confidence score.
        """
        results = model.track(frame, persist=True, tracker=self.tracker_yaml, conf=conf, classes=[0], verbose=False)
        
        active_tracks = []
        if len(results) > 0 and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.int().cpu().numpy()
            scores = results[0].boxes.conf.cpu().numpy()
            
            for box, track_id, score in zip(boxes, track_ids, scores):
                active_tracks.append({
                    "track_id": str(track_id),
                    "bbox": box.tolist(),
                    "confidence": float(score)
                })
        return active_tracks
