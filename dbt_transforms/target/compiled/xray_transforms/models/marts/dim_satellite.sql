with src as (
    select
        distinct satellite_id
    from "goes_xray_radiation_dwh"."analytical_staging"."stg_xray_telemetry"
)

select 
    md5(cast(satellite_id as text)) as satellite_sk,
    satellite_id as satellite_business_key,
    'GOES-' || (cast(satellite_id as text)) as satellite_name
from src