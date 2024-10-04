import psycopg2
import os
from src.config import MIGRATIONS_DIR, TIMESCALE_CONN_STRING

class TimescaleClient:

    def __init__(self):
        self.conn = psycopg2.connect(TIMESCALE_CONN_STRING)
        self.cur = self.conn.cursor()

    def add_stop(self, lat, lng, zero_rides, total_rides) -> None:
        self.conn.commit()
        self.cur.execute("BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        try:
            cmd = "INSERT INTO stops (lat, lng, zero_rides, total_rides) VALUES (%s, %s, %s, %s)"
            self.cur.execute(cmd, (lat, lng, zero_rides, total_rides))
            self.conn.commit()
        except psycopg2.Error:
            self.cur.execute("ROLLBACK")
            raise
    def apply_schema(self, schema_file: str) -> None:
        full_path = os.path.join(MIGRATIONS_DIR, schema_file)

        with open(full_path, 'r') as file:
            schema_sql = file.read()

        self.cur.execute(schema_sql)
        self.conn.commit()

    def get_nodes(self, time_start, time_end, zero_rides, proportion) -> list:
        self.cur.execute(f"SELECT lat, lng FROM stops;")
        nodes = [(lat, lng) for (lat, lng,) in self.cur.fetchall()]
        print(nodes)
        return nodes