import json
import time
import requests
import argparse

def replay_events(file_path: str, api_url: str, delay: float = 0.1):
    """
    Reads events from a JSONL file and replays them to the API endpoint.
    Useful for testing the backend independently of the CV engine.
    """
    print(f"Replaying events from {file_path} to {api_url}")
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                
                event_data = json.loads(line)
                
                try:
                    response = requests.post(api_url, json=event_data)
                    if response.status_code == 200 or response.status_code == 201:
                        print(f"✅ Sent: {event_data.get('event_type')} - {event_data.get('track_id')}")
                    else:
                        print(f"❌ Failed: {response.status_code} - {response.text}")
                except Exception as e:
                    print(f"❌ Connection Error: {e}")
                
                if delay > 0:
                    time.sleep(delay)
                    
    except FileNotFoundError:
        print(f"Error: Could not find file {file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Replay events.jsonl to the API")
    parser.add_argument("--file", type=str, default="events.jsonl", help="Path to events.jsonl")
    parser.add_argument("--url", type=str, default="http://localhost:8000/events/ingest", help="API Ingest URL")
    parser.add_argument("--delay", type=float, default=0.1, help="Delay between events in seconds")
    
    args = parser.parse_args()
    replay_events(args.file, args.url, args.delay)
