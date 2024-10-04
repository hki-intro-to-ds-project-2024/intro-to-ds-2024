DROP TABLE IF EXISTS stops;

CREATE TABLE stops(time TIMESTAMPTZ NOT NULL DEFAULT now(),
                        lat DOUBLE PRECISION,
                        lng DOUBLE PRECISION,
                        zero_rides INTEGER,
                        total_rides INTEGER);

SELECT create_hypertable('stops', 'time');
