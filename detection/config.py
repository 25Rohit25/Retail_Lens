from pydantic import BaseModel
from typing import List, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class ZoneConfig(BaseModel):
    name: str
    polygon: List[Tuple[int, int]]

class LineConfig(BaseModel):
    name: str
    pt1: Tuple[int, int]
    pt2: Tuple[int, int]

class AppConfig(BaseModel):
    model_path: str = "yolov8n.onnx" # Using nano by default for 8GB RAM Ryzen 5 constraint
    conf_threshold: float = 0.4
    skip_frames: int = 2
    zones: List[ZoneConfig] = []
    entry_lines: List[LineConfig] = []
    exit_lines: List[LineConfig] = []

def get_default_config() -> AppConfig:
    return AppConfig(
        zones=[
            ZoneConfig(name="billing_zone", polygon=[(100, 100), (400, 100), (400, 300), (100, 300)])
        ],
        entry_lines=[
            LineConfig(name="main_entry", pt1=(0, 50), pt2=(200, 50))
        ],
        exit_lines=[
            LineConfig(name="main_exit", pt1=(0, 60), pt2=(200, 60))
        ]
    )
