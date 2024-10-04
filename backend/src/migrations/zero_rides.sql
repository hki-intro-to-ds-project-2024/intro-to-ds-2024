CREATE TABLE stops( time TIMESTAMPTZ NOT NULL DEFAULT now(),
                        lat DOUBLE PRECISION,
                        lng DOUBLE PRECISION);

SELECT create_hypertable('stops', by_range('time'));