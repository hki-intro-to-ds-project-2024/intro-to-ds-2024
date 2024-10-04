import psycopg2
import os
from random import randint
from src.config import MIGRATIONS_DIR, TIMESCALE_CONN_STRING
from src.node import Node

class TimescaleClient:

    def __init__(self):
        self.conn = psycopg2.connect(TIMESCALE_CONN_STRING)
        self.cur = self.conn.cursor()

    def add_stop(self, node: Node) -> None:
        self.cur.execute(
            "INSERT INTO stops (lat, lng, zero_rides, total_rides) VALUES (%s, %s, %s, %s)",
            (node.coords[0], node.coords[1], randint(0,10), randint(10, 100)))
        self.conn.commit()

    def apply_schema(self, schema_file: str) -> None:
        try:
            full_path = os.path.join(MIGRATIONS_DIR, schema_file)

            with open(full_path, 'r') as file:
                schema_sql = file.read()

            self.cur.execute(schema_sql)
            self.conn.commit()
        except:
            print("Failed to apply schema, relation probably exists already")