import json
import os
from typing import Dict, Any

class StoreLayoutLoader:
    def __init__(self, layout_path: str = "store_layout.json"):
        self.layout_path = layout_path
        self.layout_data: Dict[str, Any] = {}
        self.load()

    def load(self):
        """Loads the store layout JSON file."""
        if os.path.exists(self.layout_path):
            with open(self.layout_path, "r") as f:
                self.layout_data = json.load(f)
        else:
            # Fallback/Dummy default for testing if not provided
            self.layout_data = {
                "store_id": "store_1",
                "open_hours": {"start": "09:00", "end": "21:00"},
                "zones": [
                    {
                        "zone_id": "billing_zone_1",
                        "type": "billing",
                        "polygon": [[100, 100], [200, 100], [200, 200], [100, 200]]
                    },
                    {
                        "zone_id": "entrance_1",
                        "type": "entry",
                        "polygon": [[0, 0], [50, 0], [50, 50], [0, 50]]
                    }
                ],
                "cameras": [
                    {
                        "camera_id": "cam_01",
                        "coverage": ["entrance_1", "billing_zone_1"]
                    }
                ]
            }

    def get_zone(self, zone_id: str) -> Dict[str, Any]:
        """Returns the specific zone details including its polygon."""
        for zone in self.layout_data.get("zones", []):
            if zone["zone_id"] == zone_id:
                return zone
        return {}

    def get_all_zones(self):
        """Returns all defined zones."""
        return self.layout_data.get("zones", [])

    def get_store_metadata(self):
        """Returns store-level configuration like open hours."""
        return {
            "store_id": self.layout_data.get("store_id"),
            "open_hours": self.layout_data.get("open_hours")
        }
