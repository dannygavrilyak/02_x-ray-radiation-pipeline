from datetime import datetime, timedelta, timezone

from airflow.decorators import dag, task

from src.data_from_noaa import fetch_xray_data
from src.load_to_postgres import load_raw_to_postgres

default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=3),
    "execution_timeout": timedelta(minutes=12),
}

@dag(
    dag_id='noaa_goes_xray_pipeline',
    default_args=default_args,
    start_date=datetime(2026, 5, 1, tzinfo=timezone.utc),
    catchup=False,
    schedule="@hourly",
    max_active_runs=1,
    tags=["noaa", "dwh", "telemetry"]
)

def xray_info_to_airflow():
    
    @task
    def extract_task() -> str:
        return fetch_xray_data()

    @task
    def load_data(file_path: str):
        load_raw_to_postgres(target_file=file_path)

    raw_payload = extract_task()
    load_data(raw_payload)

xray_info_to_airflow()