import requests
import json
from datetime import datetime


BASE_URL = "http://127.0.0.1:3001/api/train"


def call_api(endpoint: str, method: str = "GET", params=None, payload=None, timeout=10):
    """
    Calls the given API endpoint with provided params or payload.

    :param endpoint: API endpoint path after BASE_URL (e.g. "trainInfo")
    :param method: HTTP method (GET or POST)
    :param params: Dictionary for query parameters
    :param payload: Dictionary for JSON body
    :param timeout: Timeout in seconds
    :return: Parsed JSON or None
    """
    url = f"{BASE_URL}/{endpoint}"
    headers = {"Content-Type": "application/json"}

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        data = response.json()

        print("\n===== API CALL =====")
        print(f"Endpoint     : {endpoint}")
        print(f"Method       : {method}")
        print(f"Params       : {params}")
        print(f"Payload      : {payload}")
        print(f"Timestamp    : {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
        print("\n--- RAW RESPONSE ---")
        print(json.dumps(data, indent=4))

        return data

    except requests.exceptions.RequestException as e:
        print(f"Error calling API {endpoint}: {e}")
        return None


def get_train_info(train_number: str):
    return call_api("trainInfo/", method="GET", params={"trainNumber": train_number})


def check_pnr_status(pnr: str):
    return call_api("checkPNRStatus/", method="GET", params={"pnr": pnr})


def live_at_station(station_code: str):
    return call_api("liveAtStation", method="GET", params={"stnCode": station_code})


def track_train(train_number: str, date_str: str):
    return call_api("trackTrain", method="POST", payload={"trainNumber": train_number, "date": date_str})


def search_train_between_stations(from_code: str, to_code: str):
    return call_api("searchTrainBetweenStations", method="POST",
                    payload={"fromStnCode": from_code, "toStnCode": to_code})


if __name__ == "__main__":
    # Example usage
    get_train_info("22177")
    check_pnr_status("8135417862")
    live_at_station("NDLS")
    track_train("22177", "13-08-2025")
    search_train_between_stations("NDLS", "BCT")
