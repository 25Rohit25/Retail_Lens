import uuid
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class VisitorSession:
    def __init__(self, visitor_id: str, first_seen: datetime, initial_embedding: List[float]):
        self.visitor_id = visitor_id
        self.first_seen = first_seen
        self.last_seen = first_seen
        # Appearance gallery stores multiple embeddings to handle pose changes over time
        self.gallery: List[List[float]] = [initial_embedding]
        
    def add_embedding(self, embedding: List[float], max_gallery_size: int = 5):
        self.gallery.append(embedding)
        if len(self.gallery) > max_gallery_size:
            # Keep newest embeddings, drop oldest (FIFO)
            self.gallery.pop(0)

class SessionManager:
    def __init__(self, 
                 reid_threshold: float = 0.85, 
                 gallery_size: int = 5,
                 session_timeout_minutes: int = 60):
        """
        Manages identity and sessions for visitors.
        """
        self.reid_threshold = reid_threshold
        self.gallery_size = gallery_size
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        
        # Active sessions in memory. Key: visitor_id
        self.sessions: Dict[str, VisitorSession] = {}
        # Mapping from temporary CV track_id to persistent visitor_id. 
        self.track_to_visitor: Dict[str, str] = {}

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        v1_arr, v2_arr = np.array(v1), np.array(v2)
        norm1 = np.linalg.norm(v1_arr)
        norm2 = np.linalg.norm(v2_arr)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(v1_arr, v2_arr) / (norm1 * norm2))

    def _find_match(self, new_embedding: List[float], current_time: datetime) -> Optional[str]:
        best_match_id = None
        best_score = 0.0
        
        # Clean up expired sessions first to avoid matching against someone who left hours ago
        self._cleanup_expired_sessions(current_time)

        for visitor_id, session in self.sessions.items():
            # Compare against all embeddings in the gallery
            for gallery_emb in session.gallery:
                sim = self._cosine_similarity(new_embedding, gallery_emb)
                if sim > best_score and sim >= self.reid_threshold:
                    best_score = sim
                    best_match_id = visitor_id
                    
        if best_match_id:
            logger.debug(f"Matched to {best_match_id} with similarity {best_score:.3f}")
            
        return best_match_id

    def _cleanup_expired_sessions(self, current_time: datetime):
        expired = []
        for vid, sess in self.sessions.items():
            if current_time - sess.last_seen > self.session_timeout:
                expired.append(vid)
        for vid in expired:
            del self.sessions[vid]

    def process_detection(self, track_id: str, embedding: List[float], timestamp: datetime) -> str:
        """
        Processes a new detection and returns the persistent visitor_id.
        """
        # 1. Short Occlusion Handling: Check if we already know this track_id
        if track_id in self.track_to_visitor:
            vid = self.track_to_visitor[track_id]
            if vid in self.sessions:
                self.sessions[vid].last_seen = timestamp
                return vid

        # 2. Re-entry / Camera Overlap Handling: Match embedding against existing sessions
        matched_vid = self._find_match(embedding, timestamp)
        
        if matched_vid:
            # Same customer returning or moving to a different camera
            self.sessions[matched_vid].last_seen = timestamp
            self.sessions[matched_vid].add_embedding(embedding, self.gallery_size)
            self.track_to_visitor[track_id] = matched_vid
            logger.info(f"RE-ENTRY DETECTED: Track {track_id} -> Visitor {matched_vid}")
            return matched_vid
            
        # 3. New Session Generation / Crowded Entry Situations
        new_visitor_id = f"V_{uuid.uuid4().hex[:8].upper()}"
        self.sessions[new_visitor_id] = VisitorSession(new_visitor_id, timestamp, embedding)
        self.track_to_visitor[track_id] = new_visitor_id
        logger.info(f"NEW VISITOR: Track {track_id} -> Visitor {new_visitor_id}")
        
        return new_visitor_id
