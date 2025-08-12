import requests
import json
from datetime import datetime

def track_train(train_number: str, date_str: str):
    url = "http://127.0.0.1:3001/api/train/trackTrain"
    headers = {"Content-Type": "application/json"}
    payload = {
        "trainNumber": train_number,
        "date": date_str
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        print("\n===== LIVE TRAIN STATUS =====")
        print(f"Train Number : {train_number}")
        print(f"Date         : {date_str}")
        print(f"Last Updated : {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
        print("\n--- RAW RESPONSE ---")
        print(json.dumps(data, indent=4))
        if isinstance(data, dict):
            if "current_station" in data:
                print("\nCurrent Station:", data["current_station"])
            if "status" in data:
                print("Status:", data["status"])
            if "upcoming_stations" in data:
                print("\nUpcoming Stations:")
                for stn in data["upcoming_stations"]:
                    print(f"  - {stn}")
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching train status: {e}")
        return None

if __name__ == "__main__":
    train_number = "22177"
    travel_date = "13-08-2025"
    track_train(train_number, travel_date)
