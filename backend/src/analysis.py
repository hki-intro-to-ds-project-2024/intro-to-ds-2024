
from src.node import Node
from src.config import DATA_DIR
from src.timescale import TimescaleClient
import pandas as pd
import json

class Analytics:
    def __init__(self):
        self.nodes = self._get_node_locs()
        self._timescale_connection = TimescaleClient()
        self._timescale_connection.apply_schema("zero_rides.sql")

    def add_node(self, node: Node) -> None:
        self.nodes.append(node)

    def get_nodes_json(self) -> dict:
        return {
            i: {
                "position": node.get_node_json()
            } 
            for i, node in enumerate(self.nodes)
        }

    def _get_node_locs(self) :
        data_stops = pd.read_csv(DATA_DIR / "stops/Helsingin_ja_Espoon_kaupunkipyöräasemat_avoin.csv")
        return [Node(lat, lng) for lat, lng in zip(data_stops['y'], data_stops['x'])]

