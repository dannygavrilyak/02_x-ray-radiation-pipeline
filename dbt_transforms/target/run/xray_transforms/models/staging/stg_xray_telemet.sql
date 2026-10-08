
  create view "goes_xray_radiation_dwh"."analytics_staging"."stg_xray_telemet__dbt_tmp"
    
    
  as (
    with src as (
    select * from "goes_xray_radiation_dwh"."public"."raw_xray_telemetry"
)

select
    time_tag,
    satellite as satellite_id,
    energy as energy_channel,
    flux,
    observed_flux,
    electron_correction,
    electron_contamination as is_electron_contaminated,
    ingested_at
from src
  );