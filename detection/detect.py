import cv2
import logging
from ultralytics import YOLO
from typing import Dict, Any, Tuple
from detection.config import AppConfig, get_default_config
from detection.tracker import Tracker
from detection.zones import ZoneManager

logger = logging.getLogger(__name__)

class DetectionPipeline:
    def __init__(self, config: AppConfig):
        """
        Initializes the entire detection pipeline.
        """
        self.config = config
        logger.info(f"Loading YOLO model from {config.model_path}")
        # Initialize YOLO. Use ONNX version for CPU speed up on Ryzen 5
        self.model = YOLO(config.model_path, task='detect')
        self.tracker = Tracker()
        self.zone_manager = ZoneManager(config.zones, config.entry_lines, config.exit_lines)
        
        # Session state tracking
        self.frame_count = 0
        # Maps track_id to previous bottom_center coordinate
        self.track_history: Dict[str, Tuple[int, int]] = {} 

    def process_frame(self, frame) -> list:
        """
        Process a single frame and emit relevant events.
        """
        self.frame_count += 1
        # Hardware optimization: skip frames to maintain real-time performance
        if self.frame_count % self.config.skip_frames != 0:
            return []

        tracks = self.tracker.track(self.model, frame, self.config.conf_threshold)
        events = []
        
        for track in tracks:
            track_id = track["track_id"]
            x1, y1, x2, y2 = track["bbox"]
            bc = (int((x1 + x2) / 2), int(y2)) # Using bottom center point for precise location mapping
            
            # Staff flagging hook integration
            is_staff = self._staff_flagging_hook(track)
            
            prev_bc = self.track_history.get(track_id)
            if prev_bc is None:
                # Session Creation Event
                events.append({
                    "type": "SESSION_CREATED",
                    "track_id": track_id,
                    "confidence": track["confidence"],
                    "is_staff": is_staff,
                    "location": bc
                })
                prev_bc = bc
            
            # Zone checks
            current_zones = self.zone_manager.get_current_zones(bc)
            if current_zones:
                events.append({
                    "type": "ZONE_PRESENCE",
                    "track_id": track_id,
                    "zones": current_zones,
                    "confidence": track["confidence"]
                })

            # Line crossing logic (Entry vs Exit)
            entered, exited = self.zone_manager.check_entry_exit(prev_bc, bc)
            if entered:
                events.append({"type": "ENTRY_DETECTED", "track_id": track_id, "confidence": track["confidence"]})
            if exited:
                events.append({"type": "EXIT_DETECTED", "track_id": track_id, "confidence": track["confidence"]})
                
            self.track_history[track_id] = bc
            
        return events

    def _staff_flagging_hook(self, track: Dict[str, Any]) -> bool:
        """
        Hook for staff classification heuristics (e.g., uniform color).
        Currently defaults to False until color analysis is fully implemented.
        """
        return False
        
    def run_on_video(self, video_path: str):
        """
        Test utility to run the pipeline on a local video file.
        """
        cap = cv2.VideoCapture(video_path)
        logger.info(f"Starting pipeline on video {video_path}")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            events = self.process_frame(frame)
            if events:
                logger.debug(f"Frame {self.frame_count} events: {events}")
                    
        cap.release()
        logger.info("Video processing complete.")

if __name__ == "__main__":
    # Example usage hook
    config = get_default_config()
    pipeline = DetectionPipeline(config)
    logger.info("Pipeline initialized and ready for video.")
