# 🛰️ NOAA GOES-18 Solar X-Ray Telemetry ELT Pipeline & Kimball DWH

An automated end-to-end ELT data pipeline collecting real-time satellite telemetry of solar X-ray flux from the **NOAA Space Weather Prediction Center (GOES-18)**, loading it into an analytical data warehouse (**PostgreSQL**), transforming it into a **Kimball Star Schema via dbt Core**, enforcing data quality tests, and serving live telemetry via an interactive **Streamlit** dashboard.

---

## 🏗️ Architecture & Data Flow

```text
  [ NOAA SWPC REST API ] (Satellite GOES-18 Telemetry)
             │
             ▼  (Hourly Batch Ingestion via requests / Python)
  [ Apache Airflow 2.9 ] (TaskFlow DAG: extract_task >> load_data >> dbt_run >> dbt_test)
             │
             ▼  (Idempotent UPSERT ON CONFLICT)
  [ PostgreSQL DWH (Raw Layer) ] -> public.raw_xray_telemetry
             │
             ▼  (dbt Core Transformations)
  ┌─────────────────────────────────────────────────────────────┐
  │  dbt Core (Data Transformations & Modeling)                 │
  │                                                             │
  │  1. Staging Layer (View):                                   │
  │     └─ analytical_staging.stg_xray_telemetry                │
  │                                                             │
  │  2. Marts Layer (Kimball Star Schema Tables):               │
  │     ├─ analytical_analytics.dim_satellite (SCD Type 1)      │
  │     └─ analytical_analytics.fct_xray_telemetry (Grain Fact)│
  │                                                             │
  │  3. Data Quality Testing (PASS=8):                          │
  │     ├─ Generic Tests: unique, not_null, accepted_values,    │
  │     │                 relationships                         │
  │     └─ Singular Test: assert_flux_is_positive               │
  └─────────────────────────────────────────────────────────────┘
             │
             ▼  (Live Analytical Querying)
  [ Streamlit & Plotly Dashboard ] -> Logarithmic Flux & Solar Flare Monitoring (Port 8501)
```

---

## 🛠️ Tech Stack

* **Orchestration:** Apache Airflow 2.9.1 (TaskFlow API, LocalExecutor)
* **Database & Storage:** PostgreSQL 15 (Docker)
* **Data Transformation:** dbt Core 1.12 (`dbt-postgres`)
* **Analytics UI:** Streamlit, Plotly Express, SQLAlchemy
* **Code Quality & CI/CD:** Ruff Linter, GitHub Actions CI
* **Infrastructure:** Docker Compose (multi-container isolated network)

---

## 📐 Data Modeling (Kimball Star Schema)

### Fact Table Grain
> **Grain:** One row represents a single calibrated X-ray flux measurement from a specific satellite and energy channel at a specific UTC timestamp (`time_tag`).

* **`fct_xray_telemetry` (Fact):**
  * `telemetry_sk` (Primary Surrogate Key: `MD5(time_tag || energy_channel)`)
  * `satellite_sk` (Foreign Key referencing `dim_satellite`)
  * `energy_channel` (Degenerate Dimension: `0.05-0.4nm` / `0.1-0.8nm`)
  * `flux` (Core Metric: calibrated X-ray irradiance in $\text{W/m}^2$)
  * `observed_flux`, `electron_correction` (Sensor metrics)
  * `is_electron_contaminated` (Data flag)
  * `time_tag`, `ingested_at` (Timestamps)

* **`dim_satellite` (Dimension):**
  * `satellite_sk` (Primary Surrogate Key: `MD5(satellite_id)`)
  * `satellite_business_key` (Natural key: e.g. `18`)
  * `satellite_name` (e.g. `GOES-18`)

---

## 🧪 Data Quality Tests (`dbt test` — 8/8 PASS)

Data integrity is guarded by 8 automated tests:
1. **`unique` & `not_null`** on `dim_satellite.satellite_sk` (Primary Key constraint).
2. **`unique` & `not_null`** on `fct_xray_telemetry.telemetry_sk` (Fact Grain constraint).
3. **`not_null`** on `fct_xray_telemetry.satellite_sk`.
4. **`relationships`** (Foreign Key referential integrity between `fct_` and `dim_`).
5. **`accepted_values`** on `fct_xray_telemetry.energy_channel` (`0.05-0.4nm`, `0.1-0.8nm`).
6. **Singular Test (`assert_flux_is_positive.sql`):** verifies physical law $\text{flux} \ge 0$, guarding against negative sensor anomalies.

---

## 🚀 Quick Start (Zero-Setup)

### 1. Clone & Configure
```bash
git clone https://github.com/dannygavrilyak/02_x-ray-radiation-pipeline.git
cd 02_x-ray-radiation-pipeline
cp .env.example .env
```

### 2. Start Infrastructure
```bash
docker compose up -d
```
* **Airflow Web UI:** [http://localhost:8080](http://localhost:8080) (Credentials: `airflow` / `airflow`)
* **PostgreSQL DWH:** `localhost:5435`, Database: `goes_xray_radiation_dwh`

### 3. Launch Dashboard
```bash
# In Python virtual environment:
streamlit run app.py
```
* **Dashboard:** [http://localhost:8501](http://localhost:8501)
