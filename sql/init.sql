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