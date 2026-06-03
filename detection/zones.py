import cv2
import numpy as np
from typing import List, Tuple
from detection.config import ZoneConfig, LineConfig
import logging

logger = logging.getLogger(__name__)

class ZoneManager:
    def __init__(self, zones: List[ZoneConfig], entry_lines: List[LineConfig], exit_lines: List[LineConfig]):
        """
        Manages polygonal zones and entry/exit lines.
        """
        self.zones = zones
        self.entry_lines = entry_lines
        self.exit_lines = exit_lines

    def is_in_zone(self, point: Tuple[int, int], polygon: List[Tuple[int, int]]) -> bool:
        """Checks if a point is strictly inside a polygon."""
        poly_arr = np.array(polygon, dtype=np.int32)
        return cv2.pointPolygonTest(poly_arr, point, False) >= 0

    def get_current_zones(self, point: Tuple[int, int]) -> List[str]:
        """Returns all zone names that the point is currently within."""
        active_zones = []
        for zone in self.zones:
            if self.is_in_zone(point, zone.polygon):
                active_zones.append(zone.name)
        return active_zones

    def _crossed_line(self, pt_prev: Tuple[int, int], pt_curr: Tuple[int, int], line: LineConfig) -> bool:
        """
        Determines if a line segment (pt_prev -> pt_curr) intersects with the configured line.
        """
        def ccw(A, B, C):
            return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
        
        A, B = line.pt1, line.pt2
        C, D = pt_prev, pt_curr
        return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

    def check_entry_exit(self, pt_prev: Tuple[int, int], pt_curr: Tuple[int, int]) -> Tuple[bool, bool]:
        """
        Checks if the movement from prev to curr point crosses any entry or exit lines.
        Returns: (entered, exited) booleans.
        """
        entered = any(self._crossed_line(pt_prev, pt_curr, line) for line in self.entry_lines)
        exited = any(self._crossed_line(pt_prev, pt_curr, line) for line in self.exit_lines)
        return entered, exited
