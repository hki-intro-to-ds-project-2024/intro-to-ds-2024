import psycopg2
import os
from random import randrange
from src.config import MIGRATIONS_DIR, TIMESCALE_CONN_STRING
from src.node import Node

class TimescaleClient:

    def __init__(self):
        self.conn = psycopg2.connect(TIMESCALE_CONN_STRING)
        self.cur = self.conn.cursor()

    def add_stop(self, node: Node) -> None:
        self.conn.commit()
        self.cur.execute("BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        try:
            x = randrange(0, 10)
            y = randrange(10, 100)
            cmd = "INSERT INTO stops (lat, lng, zero_rides, total_rides) VALUES (%s, %s, %s, %s)"
            self.cur.execute(cmd, (node.coords[0], node.coords[1], x, y))
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
