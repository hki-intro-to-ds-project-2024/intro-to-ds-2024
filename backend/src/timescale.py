import psycopg2
import os
from src.config import MIGRATIONS_DIR, TIMESCALE_CONN_STRING
from src.node import Node

class TimescaleClient:

    def __init__(self):
        self.conn = psycopg2.connect(TIMESCALE_CONN_STRING)
        self.cur = self.conn.cursor()

    def add_node(self, node: Node) -> None:
        self.cur.execute(
            "INSERT INTO nodes (lat, lng) VALUES (%s, %s)",
            (node.coords[0], node.coords[1])
        )
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