# This is a wrapper around your tracking algorithm.
# In a production scenario with the full videos, you would install `lap` and `cython_bbox` 
# and use the official ByteTrack implementation here. 

import numpy as np

class TrackerWrapper:
    def __init__(self):
        self.active_tracks = {} # track_id -> centroid (x, y)
        self.feature_cache = {} 
        self.next_id = 1

    def compute_similarity(self, feat1, feat2):
        return np.dot(feat1, feat2) / (np.linalg.norm(feat1) * np.linalg.norm(feat2))
        
    def get_centroid(self, bbox):
        return ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)

    def update(self, detections, frame):
        """
        Accepts YOLO detections and handles robust tracking + Re-ID.
        """
        tracked_objects = []
        if len(detections) == 0:
            self.active_tracks.clear()
            return []
            
        current_centroids = [self.get_centroid(det[:4]) for det in detections]
        unmatched_detections = list(range(len(detections)))
        matched_tracks = {} # det_idx -> track_id
        
        # 1. Greedy Centroid Matching (Stable Tracking)
        for track_id, last_centroid in list(self.active_tracks.items()):
            best_dist = 150 # Pixel distance threshold
            best_det_idx = -1
            
            for idx in unmatched_detections:
                dist = np.linalg.norm(np.array(current_centroids[idx]) - np.array(last_centroid))
                if dist < best_dist:
                    best_dist = dist
                    best_det_idx = idx
                    
            if best_det_idx != -1:
                matched_tracks[best_det_idx] = track_id
                unmatched_detections.remove(best_det_idx)
                self.active_tracks[track_id] = current_centroids[best_det_idx]
            else:
                del self.active_tracks[track_id] # Track lost
                
        # 2. Handle New Detections & Re-ID
        for idx in unmatched_detections:
            # Stub visual features. We randomize here to mock different appearances.
            current_features = np.random.rand(128) 
            
            matched_visitor_id = None
            best_sim = 0.0
            
            for cached_id, cached_feat in self.feature_cache.items():
                sim = self.compute_similarity(current_features, cached_feat)
                if sim > 0.85 and sim > best_sim:
                    best_sim = sim
                    matched_visitor_id = cached_id
                    
            if not matched_visitor_id:
                # Genuinely new visitor
                matched_visitor_id = f"VIS_TRACK_{self.next_id}"
                self.next_id += 1
                
            self.feature_cache[matched_visitor_id] = current_features
            self.active_tracks[matched_visitor_id] = current_centroids[idx]
            matched_tracks[idx] = matched_visitor_id
            
        # Build Output
        for i, det in enumerate(detections):
            track_id = matched_tracks[i]
            # Flag Re-entry only on the first frame it reappears
            is_reentry = (track_id in self.feature_cache and i in unmatched_detections and track_id != f"VIS_TRACK_{self.next_id - 1}")
            
            tracked_objects.append({
                "track_id": track_id,
                "bbox": det[:4],
                "confidence": det[4],
                "is_reentry": is_reentry
            })
            
        return tracked_objects
