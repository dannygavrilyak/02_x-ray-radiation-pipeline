import os

import pandas as pd
import plotly.express as pe
import streamlit as sl
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

sl.set_page_config(
    page_title="NOAA GOES-18 🛰️ Solar X-Ray Telemetry Monitor", page_icon="📡", layout="wide"
)

DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5435"))


@sl.cache_data(ttl=65)
def load_data():
    db_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(db_url)

    query = """
        SELECT *
        FROM (
            SELECT time_tag, energy_channel, flux, is_electron_contaminated
            FROM analytical_analytics.fct_xray_telemetry
            ORDER BY time_tag DESC
            LIMIT 1000
        ) as latest_subquery
        ORDER BY time_tag ASC;
    """
    return pd.read_sql(query, engine)


try:
    df = load_data()

    sl.title("☀️ NOAA GOES X-Ray Flux Telemetry")

    col1, col2, col3 = sl.columns(3)
    col1.metric("Total measures", len(df))
    col2.metric("Max flow", f"{df['flux'].max():.2e} W/m²")
    col3.metric("Last measure (UTC)", str(df["time_tag"].max()))

    flib = pe.line(
        df,
        x="time_tag",
        y="flux",
        color="energy_channel",
        title="The sun's x-ray flow (GOES-18)",
    )
    flib.update_yaxes(type="log")
    sl.plotly_chart(flib, use_container_width=True)

    sl.dataframe(df.tail(20), use_container_width=True)

except Exception as e:  # noqa: BLE001
    sl.error(f"Error loading from DB Postgres: {e}")
