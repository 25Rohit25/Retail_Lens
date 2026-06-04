@echo off
echo Starting Store Intelligence Detection Pipeline...

echo [1/2] Processing Store 1 (STORE_BLR_002)...
python pipeline\detect.py --video "data\Store 1\Store 1\CAM 3 - entry.mp4" --layout "data\store_layout.json" --camera CAM_ENTRY_01 --store STORE_BLR_002
python pipeline\detect.py --video "data\Store 1\Store 1\CAM 1 - zone.mp4" --layout "data\store_layout.json" --camera CAM_FLOOR_01 --store STORE_BLR_002
python pipeline\detect.py --video "data\Store 1\Store 1\CAM 5 - billing.mp4" --layout "data\store_layout.json" --camera CAM_BILLING_01 --store STORE_BLR_002

echo [2/2] Processing Store 2 (STORE_MUM_001)...
python pipeline\detect.py --video "data\Store 2\Store 2\entry 1.mp4" --layout "data\store_layout.json" --camera CAM_ENTRY_01 --store STORE_MUM_001
python pipeline\detect.py --video "data\Store 2\Store 2\entry 2.mp4" --layout "data\store_layout.json" --camera CAM_ENTRY_02 --store STORE_MUM_001
python pipeline\detect.py --video "data\Store 2\Store 2\zone.mp4" --layout "data\store_layout.json" --camera CAM_FLOOR_01 --store STORE_MUM_001
python pipeline\detect.py --video "data\Store 2\Store 2\billing_area.mp4" --layout "data\store_layout.json" --camera CAM_BILLING_01 --store STORE_MUM_001

echo Pipeline finished. All events emitted to API.
pause
