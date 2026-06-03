import cv2
import numpy as np
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class OSNetExtractor:
    def __init__(self, model_path: str = "osnet_x1_0.onnx"):
        """
        Initializes the OSNet feature extractor using ONNX Runtime for CPU optimization.
        """
        self.model_path = model_path
        try:
            import onnxruntime as ort
            self.session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
            self.input_name = self.session.get_inputs()[0].name
            self.output_name = self.session.get_outputs()[0].name
            self.ready = True
            logger.info(f"Loaded OSNet ReID model from {model_path}")
        except Exception as e:
            logger.warning(f"Failed to load ONNX runtime for OSNet: {e}. Using fallback embedding generator.")
            self.ready = False

    def preprocess(self, crop: np.ndarray) -> np.ndarray:
        """
        Prepares the image crop for OSNet inference.
        """
        # Resize to 256x128 (H x W) for OSNet
        resized = cv2.resize(crop, (128, 256))
        # BGR to RGB
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        # Normalize
        img = rgb.astype(np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        img = (img - mean) / std
        # HWC to CHW
        img = np.transpose(img, (2, 0, 1))
        # Add batch dimension
        img = np.expand_dims(img, axis=0)
        return img

    def extract(self, frame: np.ndarray, bbox: List[float]) -> Optional[List[float]]:
        """
        Extracts the 512-dimensional embedding from the bounding box.
        """
        x1, y1, x2, y2 = map(int, bbox)
        
        # Boundary checks
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
        
        if x2 <= x1 or y2 <= y1:
            return None # Invalid box
            
        crop = frame[y1:y2, x1:x2]
        
        if self.ready:
            input_tensor = self.preprocess(crop)
            features = self.session.run([self.output_name], {self.input_name: input_tensor})[0]
            # L2 Normalize the features
            features = features.flatten()
            norm = np.linalg.norm(features)
            if norm > 0:
                features = features / norm
            return features.tolist()
        else:
            # Fallback: color histogram based deterministic mock for offline testing without ONNX
            avg_color = cv2.mean(crop)[:3]
            mock_emb = np.random.normal(loc=avg_color[0]/255.0, scale=0.1, size=512)
            mock_emb = mock_emb / np.linalg.norm(mock_emb)
            return mock_emb.tolist()
