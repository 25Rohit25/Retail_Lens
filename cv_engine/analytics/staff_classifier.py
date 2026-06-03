from typing import Dict, Any, List
import datetime

class StaffClassifier:
    def __init__(self, min_daily_duration: int = 14400, min_appearances: int = 50):
        """
        Heuristic-based staff classifier.
        Args:
            min_daily_duration: Minimum seconds seen in a day to be considered staff (e.g., 4 hours).
            min_appearances: Minimum number of unique sessions/tracks in a day.
        """
        self.min_daily_duration = min_daily_duration
        self.min_appearances = min_appearances
        
        # In-memory tracking for heuristic analysis. 
        # In production, this data would be fetched from the PostgreSQL database.
        self.visitor_stats: Dict[str, Dict[str, Any]] = {}

    def update_stats(self, visitor_id: str, dwell_time: float, track_event: bool = False):
        """
        Updates the daily statistics for a visitor.
        """
        if visitor_id not in self.visitor_stats:
            self.visitor_stats[visitor_id] = {
                "total_duration": 0.0,
                "appearances": 0
            }
            
        self.visitor_stats[visitor_id]["total_duration"] += dwell_time
        if track_event:
            self.visitor_stats[visitor_id]["appearances"] += 1

    def is_staff(self, visitor_id: str, uniform_color_match: bool = False) -> bool:
        """
        Determines if a visitor is a staff member based on heuristics.
        """
        stats = self.visitor_stats.get(visitor_id, {"total_duration": 0.0, "appearances": 0})
        
        condition_1 = stats["total_duration"] >= self.min_daily_duration
        condition_2 = stats["appearances"] >= self.min_appearances
        
        # Rule: Uniform color + frequent appearance OR long daily presence
        return (uniform_color_match and condition_2) or condition_1

    def evaluate_all(self) -> List[str]:
        """Returns a list of visitor_ids identified as staff."""
        staff_list = []
        for vid, stats in self.visitor_stats.items():
            if self.is_staff(vid):
                staff_list.append(vid)
        return staff_list
