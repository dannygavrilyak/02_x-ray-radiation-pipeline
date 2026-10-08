from datetime import datetime, timedelta, timezone

from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator

from src.data_from_noaa import fetch_xray_data
from src.load_to_postgres import load_raw_to_postgres

default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=3),
    "execution_timeout": timedelta(minutes=12),
}


@dag(
    dag_id="noaa_goes_xray_pipeline",
    default_args=default_args,
    start_date=datetime(2026, 5, 1, tzinfo=timezone.utc),
    catchup=False,
    schedule="@hourly",
    max_active_runs=1,
    tags=["noaa", "dwh", "telemetry"],
)
def xray_info_to_airflow():

    @task
    def extract_task() -> str:
        return fetch_xray_data()

    @task
    def load_data(file_path: str):
        load_raw_to_postgres(target_file=file_path)

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt_transforms && dbt run --profiles-dir .",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/dbt_transforms && dbt test --profiles-dir .",
    )

    raw_payload = extract_task()
    load_step = load_data(raw_payload)

    load_step >> dbt_run >> dbt_test


xray_info_to_airflow()
