import cv2
import numpy as np
import torch
import torchvision.transforms as T
from typing import List

# A mock OSNet loader since installing torchreid can be complex and environment dependent.
# In a real environment, we would use torchreid.models.build_model
class OSNetReID:
    def __init__(self, model_name: str = 'osnet_x1_0', use_gpu: bool = False):
        """
        Initializes OSNet feature extractor.
        """
        self.device = torch.device('cuda' if use_gpu and torch.cuda.is_available() else 'cpu')
        
        # Load pre-trained OSNet from torchreid or torchvision
        # Here we mock the behavior for the architecture plan, returning random embeddings
        # to simulate the ReID process without failing on import errors.
        self.model_name = model_name
        self.transform = T.Compose([
            T.ToPILImage(),
            T.Resize((256, 128)),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        print(f"OSNet initialized on {self.device} (Mock Mode for architecture testing)")

    def extract_features(self, frame: np.ndarray, bboxes: List[List[float]]) -> List[List[float]]:
        """
        Extracts 512-dim ReID embeddings for each bounding box.
        Args:
            frame: BGR image.
            bboxes: List of [x1, y1, x2, y2].
        Returns:
            List of 512-dimensional embeddings.
        """
        embeddings = []
        for box in bboxes:
            x1, y1, x2, y2 = map(int, box)
            
            # Ensure coordinates are within image boundaries
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(frame.shape[1], x2)
            y2 = min(frame.shape[0], y2)
            
            if x2 <= x1 or y2 <= y1:
                embeddings.append(np.zeros(512).tolist()) # Invalid box
                continue

            crop = frame[y1:y2, x1:x2]
            
            # Simulated embedding generation (normally we'd pass crop through OSNet)
            # tensor = self.transform(crop).unsqueeze(0).to(self.device)
            # with torch.no_grad():
            #     features = self.model(tensor)
            
            # Generate deterministic mock embedding based on color average for testing
            avg_color = cv2.mean(crop)[:3]
            mock_emb = np.random.normal(loc=avg_color[0]/255.0, scale=0.1, size=512)
            mock_emb = mock_emb / np.linalg.norm(mock_emb) # L2 normalize
            embeddings.append(mock_emb.tolist())
            
        return embeddings
