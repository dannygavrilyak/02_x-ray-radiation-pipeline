import json
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("DB_HOST", "postgres_dwh")
DB_PORT = int(os.getenv("DB_PORT", "5432"))

INSERT_QUERY = """
INSERT INTO raw_xray_telemetry (
    time_tag,
    satellite,
    flux,
    observed_flux,
    electron_correction,
    electron_contamination,
    energy,
    raw_payload
)

VALUES %s
ON CONFLICT(time_tag, energy) DO NOTHING;
"""


def get_latest_raw_file(raw_dir: str = "data/raw") -> Path:
    raw_path = Path(raw_dir)
    files = list(raw_path.glob("*.json"))
    if not files:
        raise FileNotFoundError(f"In the directory {raw_dir} no such JSON files.")
    return max(files, key=os.path.getmtime)


def load_raw_to_postgres(target_file: str | Path | None = None):

    if target_file is None:
        target_file = get_latest_raw_file()

    print(f"Reading file: {target_file}")

    with open(target_file, "r", encoding="utf-8") as f:
        records = json.load(f)

    if not isinstance(records, list):
        raise TypeError("Expected list of JSONs.")

    batch = []
    for it in records:
        time_tag = it.get("time_tag")
        if not time_tag:
            continue

        batch.append(
            (
                time_tag,
                it.get("satellite"),
                it.get("flux"),
                it.get("observed_flux"),
                it.get("electron_correction"),
                it.get("electron_contaminaton"),
                it.get("energy"),
                json.dumps(it),
            )
        )
    if not batch:
        print("It's nothing to save.")
        return

    with (
        psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
        ) as conn,
        conn.cursor() as curs,
    ):
        execute_values(curs, INSERT_QUERY, batch)
    print(f"Records processed: {len(batch)} ✅ ")


if __name__ == "__main__":
    load_raw_to_postgres()
