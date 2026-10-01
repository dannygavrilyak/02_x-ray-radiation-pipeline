import json
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5435"))
DB_NAME = os.getenv("DB_NAME", "goes_xray_radiation_dwh")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD", "postgres")

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS raw_xray_telemetry (
    time_tag TIMESTAMP WITH TIME ZONE,
    satellite INTEGER,
    flux DOUBLE PRECISION,
    observed_flux DOUBLE PRECISION,
    electron_correction DOUBLE PRECISION,
    electron_contaminaton BOOLEAN,
    energy VARCHAR(20),
    raw_payload JSONB,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (time_tag, energy)
);
"""

INSERT_QUERY = """
INSERT INTO raw_xray_telemetry (
    time_tag,
    satellite,
    flux,
    observed_flux,
    electron_correction,
    electron_contaminaton,
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


def load_raw_to_postgres():
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
        curs.execute(CREATE_TABLE)
        execute_values(curs, INSERT_QUERY, batch)
    print(f"Records processed: {len(batch)} ✅ ")


if __name__ == "__main__":
    load_raw_to_postgres()
