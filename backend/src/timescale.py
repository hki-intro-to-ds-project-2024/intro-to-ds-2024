import psycopg2
import os
import logging
from src.config import MIGRATIONS_DIR, TIMESCALE_CONN_STRING

class TimescaleClient:

    def __init__(self, logger):
        self.conn = psycopg2.connect(TIMESCALE_CONN_STRING)
        self.cur = self.conn.cursor()
        self.logger = logger

    def add_stops(self, stops) -> None:
        self.conn.commit()
        self.cur.execute("BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        try:
            cmd = "INSERT INTO stops (stop_name, lat, lng) VALUES (%s, %s, %s)"
            self.cur.executemany(cmd, stops)
            self.conn.commit()
        except psycopg2.Error as e:
            self.cur.execute("ROLLBACK")
            print(e)
            raise

    def add_rides(self, nodes) -> None:
        self.conn.commit()
        try:
            cmd = "INSERT INTO rides (time, lat, lng, zero_rides, total_rides) VALUES (%s, %s, %s, %s, %s)"
            self.cur.executemany(cmd, nodes)
            self.conn.commit()
        except psycopg2.Error as e:
            print(e)
            raise


    def apply_schema(self, schema_file: str) -> None:
        
        full_path = os.path.join(MIGRATIONS_DIR, schema_file)

        with open(full_path, 'r') as file:
            schema_sql = file.read()

        self.cur.execute(schema_sql)
        self.conn.commit()

    def get_nodes(self, time_start, time_end, zero_rides, proportion) -> list:
        cmd = f"""SELECT lat, lng FROM stops WHERE zero_rides >= {zero_rides} 
            AND total_rides > 0 AND (zero_rides * 1.0 / total_rides) >= {proportion}
            AND time >= '{time_start}' AND time < '{time_end}';"""
        try:
            self.cur.execute(cmd)
            nodes = [(lat, lng) for (lat, lng,) in self.cur.fetchall()]
            print(cmd)
            return nodes
        except:
            print("Invalid query", cmd)
            return []
