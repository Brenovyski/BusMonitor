CREATE DATABASE labredes;
CREATE SCHEMA labredes.tracking;
CREATE TABLE labredes.tracking.locations (timestamp TIMESTAMPTZ NOT NULL, bus_id TEXT NOT NULL, latitude DOUBLE PRECISION NOT NULL, longitude DOUBLE PRECISION NOT NULL, _updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW());
ALTER TABLE labredes.tracking.locations
ADD CONSTRAINT pk_locations primary key (timestamp, bus_id);