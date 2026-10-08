select flux from {{ ref('fct_xray_telemetry')}}
where flux < 0
