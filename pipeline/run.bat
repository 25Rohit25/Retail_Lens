@echo off
echo Starting Store Intelligence Detection Pipeline...

python pipeline\detect.py --video "data\Store 1\Store 1\CAM 3 - entry.mp4" --layout "data\store_layout.json" --camera CAM_ENTRY_01
python pipeline\detect.py --video "data\Store 1\Store 1\CAM 1 - zone.mp4" --layout "data\store_layout.json" --camera CAM_FLOOR_01
python pipeline\detect.py --video "data\Store 1\Store 1\CAM 5 - billing.mp4" --layout "data\store_layout.json" --camera CAM_BILLING_01

echo Pipeline finished. All events emitted to API.
pause
