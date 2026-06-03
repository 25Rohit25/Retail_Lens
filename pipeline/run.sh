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

echo "[1/3] Processing Entrance Camera..."
python pipeline/detect.py --video "$DATA_DIR/CAM 3 - entry.mp4" --layout "$LAYOUT_PATH" --camera CAM_ENTRY_01

echo "[2/3] Processing Aisle Camera..."
python pipeline/detect.py --video "$DATA_DIR/CAM 1 - zone.mp4" --layout "$LAYOUT_PATH" --camera CAM_AISLE_01

echo "[3/3] Processing Billing Camera..."
python pipeline/detect.py --video "$DATA_DIR/CAM 5 - billing.mp4" --layout "$LAYOUT_PATH" --camera CAM_BILLING_01

echo "========================================================"
echo "  PIPELINE COMPLETE. ALL EVENTS INGESTED TO DATABASE.   "
echo "========================================================"
