#!/bin/bash
# Store Intelligence Platform - Linux Pipeline Harness
# This script executes the detection pipeline on all test videos sequentially.

echo "========================================================"
echo "    STORE INTELLIGENCE - CV PIPELINE HARNESS (LINUX)    "
echo "========================================================"

# Create absolute paths for robust execution
BASE_DIR="$(pwd)"
DATA_DIR="$BASE_DIR/data"
LAYOUT_PATH="$DATA_DIR/store_layout.json"

# Activate python virtual environment if you have one, or just use system python
# source venv/bin/activate

echo "[1/2] Processing Store 1 (STORE_BLR_002)..."
python pipeline/detect.py --video "$DATA_DIR/Store 1/Store 1/CAM 3 - entry.mp4" --layout "$LAYOUT_PATH" --camera CAM_ENTRY_01 --store STORE_BLR_002
python pipeline/detect.py --video "$DATA_DIR/Store 1/Store 1/CAM 1 - zone.mp4" --layout "$LAYOUT_PATH" --camera CAM_FLOOR_01 --store STORE_BLR_002
python pipeline/detect.py --video "$DATA_DIR/Store 1/Store 1/CAM 5 - billing.mp4" --layout "$LAYOUT_PATH" --camera CAM_BILLING_01 --store STORE_BLR_002

echo "[2/2] Processing Store 2 (STORE_MUM_001)..."
python pipeline/detect.py --video "$DATA_DIR/Store 2/Store 2/entry 1.mp4" --layout "$LAYOUT_PATH" --camera CAM_ENTRY_01 --store STORE_MUM_001
python pipeline/detect.py --video "$DATA_DIR/Store 2/Store 2/entry 2.mp4" --layout "$LAYOUT_PATH" --camera CAM_ENTRY_02 --store STORE_MUM_001
python pipeline/detect.py --video "$DATA_DIR/Store 2/Store 2/zone.mp4" --layout "$LAYOUT_PATH" --camera CAM_FLOOR_01 --store STORE_MUM_001
python pipeline/detect.py --video "$DATA_DIR/Store 2/Store 2/billing_area.mp4" --layout "$LAYOUT_PATH" --camera CAM_BILLING_01 --store STORE_MUM_001

echo "========================================================"
echo "  PIPELINE COMPLETE. ALL EVENTS INGESTED TO DATABASE.   "
echo "========================================================"
