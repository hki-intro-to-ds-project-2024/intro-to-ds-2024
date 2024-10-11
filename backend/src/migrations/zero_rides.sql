DROP TABLE IF EXISTS stops;
DROP TABLE IF EXISTS rides;

CREATE TABLE stops(id SERIAL PRIMARY KEY,
                        lat DOUBLE PRECISION,
                        lng DOUBLE PRECISION,
                        stop_name VARCHAR);

CREATE TABLE rides(time TIMESTAMPTZ NOT NULL DEFAULT now(),
                        lat DOUBLE PRECISION,
                        lng DOUBLE PRECISION,
                        zero_rides BIGINT,
                        zero_proportion BIGINT);

SELECT create_hypertable('rides', 'time');
