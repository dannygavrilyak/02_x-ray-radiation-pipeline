with src as (
    select * from {{source('raw_data', 'raw_xray_telemetry')}}
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