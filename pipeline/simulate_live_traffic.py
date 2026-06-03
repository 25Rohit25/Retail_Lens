import time
import requests
import uuid
import random
from datetime import datetime

API_URL = "http://localhost:8000/events/ingest"

def send_event(event_type: str, visitor_id: str, zone_id: str = None):
    payload = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "visitor_id": visitor_id,
        "zone_id": zone_id
    }
    try:
        res = requests.post(API_URL, json=payload)
        if res.status_code == 201:
            print(f"✅ Sent {event_type} for {visitor_id}")
        else:
            print(f"❌ API Error ({res.status_code}): {res.text}")
    except Exception as e:
        print(f"❌ Connection error (Is Docker running?): {e}")

print("🛍️ Simulating Live CCTV Event Traffic...")
print("Press Ctrl+C to stop.\n")

while True:
    visitor_id = f"V_{random.randint(1000, 9999)}"
    
    # 1. Visitor Enters
    send_event("ENTRY", visitor_id)
    time.sleep(random.uniform(0.5, 1.5))
    
    # 2. Zone interaction (70% probability)
    if random.random() < 0.7:
        send_event("ZONE_ENTER", visitor_id, zone_id="aisle_1")
        time.sleep(random.uniform(1.0, 2.0))
        
        # 3. Queue Join (50% probability after zone)
        if random.random() < 0.5:
            send_event("BILLING_QUEUE_JOIN", visitor_id, zone_id="billing_1")
            time.sleep(random.uniform(1.0, 3.0))
            
            # 4. Abandon (30%) or Purchase (70%)
            if random.random() < 0.3:
                send_event("BILLING_QUEUE_ABANDON", visitor_id, zone_id="billing_1")
                print("🚨 Queue abandoned!")
            else:
                # Normal checkout
                send_event("ZONE_EXIT", visitor_id, zone_id="billing_1")
    
    # 5. Visitor Exits
    send_event("EXIT", visitor_id)
    print("---")
    time.sleep(random.uniform(1.0, 3.0))
