import json
import os
from datetime import datetime, timezone

import requests
from requests.exceptions import RequestException

URL = "https://services.swpc.noaa.gov/json/goes/primary/xrays-6-hour.json"
RAW_DIR = "data/raw"


def fetch_xray_data() -> str:
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        os.makedirs(RAW_DIR, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        filename = f"xray_{timestamp}.json"
        filepath = os.path.join(RAW_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=5)

        print(f"Raw data ({len(data)}) notes were successfully saved to: {filepath}")
        return filepath

    except RequestException as e:
        print(f"Web request error: {e}")
        raise

if __name__ == "__main__":
    fetch_xray_data() 