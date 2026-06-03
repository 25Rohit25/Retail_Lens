import cv2
import numpy as np
from ultralytics import YOLO

class YOLOv8Detector:
    def __init__(self, model_path: str = "yolov8m.onnx", conf_thresh: float = 0.5, classes: list = [0]):
        """
        Initializes the YOLOv8 detector.
        Args:
            model_path: Path to the model (preferably .onnx for CPU).
            conf_thresh: Confidence threshold for detections.
            classes: List of class IDs to detect (0 is person in COCO).
        """
        self.model = YOLO(model_path, task='detect')
        self.conf_thresh = conf_thresh
        self.classes = classes
        self.frame_count = 0

    def detect(self, frame: np.ndarray, skip_frames: int = 2):
        """
        Runs detection on a frame with frame skipping optimization.
        Args:
            frame: BGR image numpy array.
            skip_frames: Process 1 out of every `skip_frames` frames.
        Returns:
            boxes (List[List[float]]): [x1, y1, x2, y2]
            scores (List[float]): Confidence scores
            class_ids (List[int]): Class IDs
        """
        self.frame_count += 1
        if self.frame_count % skip_frames != 0:
            return [], [], [] # Skip this frame

        # Run inference. ultralytics automatically uses ONNX if model_path ends in .onnx
        results = self.model(frame, conf=self.conf_thresh, classes=self.classes, verbose=False)
        
        boxes = []
        scores = []
        class_ids = []

        if len(results) > 0:
            result = results[0]
            boxes = result.boxes.xyxy.cpu().numpy().tolist()
            scores = result.boxes.conf.cpu().numpy().tolist()
            class_ids = result.boxes.cls.cpu().numpy().tolist()

        return boxes, scores, class_ids
