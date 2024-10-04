
from src.config import DATA_DIR
from src.timescale import TimescaleClient
from random import randrange
from time import sleep
import pandas as pd
import json

class Analytics:
    def __init__(self):
        self._timescale_connection = TimescaleClient()
        print("Timescale connection initialized")
        self._timescale_connection.apply_schema("zero_rides.sql")
        self._nodes_to_timescale()
        print("nodes in timescale")

    def _nodes_to_timescale(self):
        data_stops = pd.read_csv(DATA_DIR / "stops/Helsingin_ja_Espoon_kaupunkipyöräasemat_avoin.csv")
        for node in [(lat, lng, randrange(0, 10), randrange(10, 100)) for lat, lng in zip(data_stops['y'], data_stops['x'])]:
            self._timescale_connection.add_stop(node[0], node[1], node[2], node[3])

    def get_nodes_json(self, time_start, time_end, zero_rides, proportion):
        node_list = self._timescale_connection.get_nodes(time_start, time_end, zero_rides, proportion)
        nodes = []
        for i, node in enumerate(node_list):
            nodes.append({
                'position': {'lat': node[0], 'lng': node[1]},
                'id': i,
                'type': 'pin',
                'zIndex': i
            })
        return nodes

            