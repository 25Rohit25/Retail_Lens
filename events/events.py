import json
from datetime import datetime
from typing import Dict, Optional, List
from schemas import Event, EventType

class EventEngine:
    def __init__(self, output_file: str = "events.jsonl"):
        """
        Engine responsible for generating, validating, and persisting events.
        """
        self.output_file = output_file
        # Track when a visitor entered a specific zone to calculate dwell time
        self.zone_entry_times: Dict[str, Dict[str, datetime]] = {} # visitor_id -> {zone_id: enter_time}

    def emit(self, event: Event) -> dict:
        """
        Validates (implicitly via Pydantic) and writes the event to the JSONL file.
        """
        event_dict = event.model_dump()
        event_dict['timestamp'] = event_dict['timestamp'].isoformat()
        
        with open(self.output_file, 'a') as f:
            f.write(json.dumps(event_dict) + '\n')
            
        return event_dict

    def generate_zone_enter(self, visitor_id: str, zone_id: str, track_id: str) -> Event:
        """Helper to generate Zone Enter or Billing Queue Join events."""
        event = Event(
            event_type="BILLING_QUEUE_JOIN" if "billing" in zone_id.lower() else "ZONE_ENTER",
            visitor_id=visitor_id,
            track_id=track_id,
            zone_id=zone_id
        )
        
        if visitor_id not in self.zone_entry_times:
            self.zone_entry_times[visitor_id] = {}
        self.zone_entry_times[visitor_id][zone_id] = event.timestamp
        
        self.emit(event)
        return event

    def generate_zone_exit(self, visitor_id: str, zone_id: str, track_id: str) -> List[Event]:
        """Helper to generate Zone Exit, Queue Abandonment, and calculate Dwell times."""
        events_emitted = []
        
        # Calculate dwell time
        enter_time = self.zone_entry_times.get(visitor_id, {}).get(zone_id)
        dwell_time = None
        if enter_time:
            dwell_time = (datetime.utcnow() - enter_time).total_seconds()
            del self.zone_entry_times[visitor_id][zone_id]
            
            # Emit DWELL event
            dwell_event = Event(
                event_type="ZONE_DWELL",
                visitor_id=visitor_id,
                track_id=track_id,
                zone_id=zone_id,
                dwell_time_seconds=dwell_time
            )
            self.emit(dwell_event)
            events_emitted.append(dwell_event)

        # Emit the actual EXIT or ABANDON event
        exit_type = "BILLING_QUEUE_ABANDON" if "billing" in zone_id.lower() else "ZONE_EXIT"
        exit_event = Event(
            event_type=exit_type,
            visitor_id=visitor_id,
            track_id=track_id,
            zone_id=zone_id
        )
        self.emit(exit_event)
        events_emitted.append(exit_event)
        
        return events_emitted

def print_example_outputs():
    """Generates and prints example outputs as requested by the prompt."""
    
    # Example 1: Standard Entry
    e1 = Event(event_type="ENTRY", visitor_id="V_123", track_id="T1")
    
    # Example 2: Zone Dwell
    e2 = Event(event_type="ZONE_DWELL", visitor_id="V_123", zone_id="aisle_4", dwell_time_seconds=45.5)
    
    # Example 3: Queue Abandonment
    e3 = Event(event_type="BILLING_QUEUE_ABANDON", visitor_id="V_123", zone_id="billing_1")
    
    print("--- Example Event Outputs (UUID4 generated automatically) ---")
    print("1. ENTRY Event:")
    print(json.dumps(e1.model_dump(mode='json'), indent=2))
    
    print("\n2. ZONE_DWELL Event:")
    print(json.dumps(e2.model_dump(mode='json'), indent=2))
    
    print("\n3. BILLING_QUEUE_ABANDON Event:")
    print(json.dumps(e3.model_dump(mode='json'), indent=2))

if __name__ == "__main__":
    print_example_outputs()
