from src.config import MIGRATIONS_DIR, TIMESCALE_CONN_STRING

from sqlalchemy import create_engine

import psycopg2
import os
import logging
import pandas as pd

class TimescaleClient:

    def __init__(self, logger):
        self.conn = psycopg2.connect(TIMESCALE_CONN_STRING)
        self.cur = self.conn.cursor()
        self._logger = logger

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
            cmd = "INSERT INTO rides (time, lat, lng, zero_rides, zero_proportion) VALUES (%s, %s, %s, %s, %s)"
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
        cmd = f"""SELECT DISTINCT lat, lng FROM rides WHERE zero_rides >= {zero_rides} 
            AND total_rides > 0 AND zero_proportion >= {proportion}
            AND time >= '{time_start}' AND time < '{time_end}';"""
        try:
            self.cur.execute(cmd)
            nodes = [(lat, lng) for (lat, lng,) in self.cur.fetchall()]
            print(cmd)
            return nodes
        except:
            print("Invalid query", cmd)
            return []

    def get_zero_rides(self):
        self._logger.info("Running Query")
        
        query = """
        SELECT
            date_trunc('hour', rides.time) AS interval_start,
            stops.stop_name,
            COUNT(*) AS ride_count,
            SUM(rides.zero_rides) AS zero_rides
        FROM 
            rides 
        INNER JOIN
            stops ON rides.lat = stops.lat AND rides.lng = stops.lng
        WHERE rides.time BETWEEN '2016-06-01' AND '2025-01-01'
        GROUP BY interval_start, stops.stop_name
        ORDER BY interval_start, stops.stop_name;
        """
        
        try:
            self.cur.execute(query)
            results = self.cur.fetchall()
            columns = [desc[0] for desc in self.cur.description]
            return pd.DataFrame(results, columns=columns)
        except psycopg2.Error as e:
            self._logger.error(f"Error fetching zero rides: {e}")
            return pd.DataFrame() 

    def get_stop_names(self):
        query = "SELECT DISTINCT stop_name FROM stops"
        
        try:
            self.cur.execute(query)
            results = self.cur.fetchall()
            return pd.DataFrame(results, columns=["stop_name"]) 
        except psycopg2.Error as e:
            self._logger.error(f"Error fetching stop names: {e}")
            return pd.DataFrame() 

