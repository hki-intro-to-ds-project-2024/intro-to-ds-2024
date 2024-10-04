
from src.node import Node
from src.config import DATA_DIR
from src.timescale import TimescaleClient
from time import sleep
import pandas as pd
import json

class Analytics:
    def __init__(self):
        self.nodes = self._get_node_locs()
        self._timescale_connection = TimescaleClient()
        print("Timescale connection initialized")
        sleep(2)
        self._timescale_connection.apply_schema("zero_rides.sql")
        sleep(2)
        self._nodes_to_timescale()
        print("nodes in timescale")

    def add_node(self, node: Node) -> None:
        self.nodes.append(node)

    def get_nodes_json(self) -> dict:
        return {
            i: {
                "position": node.get_node_json()
            } 
            for i, node in enumerate(self.nodes)
        }

    def _get_node_locs(self):
        data_stops = pd.read_csv(DATA_DIR / "stops/Helsingin_ja_Espoon_kaupunkipyöräasemat_avoin.csv")
        return [Node(lat, lng) for lat, lng in zip(data_stops['y'], data_stops['x'])]

    def _nodes_to_timescale(self):
        for node in self.nodes:
            self._timescale_connection.add_stop(node)
