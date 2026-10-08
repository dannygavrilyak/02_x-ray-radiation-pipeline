with stg as (
    select * from "goes_xray_radiation_dwh"."analytical_staging"."stg_xray_telemetry"
)
, dim as (
    select * from "goes_xray_radiation_dwh"."analytical_analytics"."dim_satellite"
)

select 

    md5(cast(stg.time_tag as text) || stg.energy_channel) as telemetry_sk,
    dim.satellite_sk as satellite_sk,
    stg.energy_channel as energy_channel,
    stg.flux, stg.observed_flux, stg.electron_correction, 
    stg.is_electron_contaminated, stg.time_tag, stg.ingested_at
    
from stg
left join dim 
    on stg.satellite_id = dim.satellite_business_key