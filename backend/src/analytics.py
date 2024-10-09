
from src.config import DATA_DIR
from src.timescale import TimescaleClient
from random import randrange
from time import sleep
from prophet import Prophet
from concurrent.futures import ProcessPoolExecutor
import pandas as pd
import json
import logging

class Analytics:
    def __init__(self, logger):
        self._logger = logger
        self._timescale_connection = TimescaleClient()
        self__model = Prophet()
        self._logger.info("Timescale connection initialized")
        self._timescale_connection.apply_schema("zero_rides.sql")
        self._stops_to_timescale()
        self._logger.info("stops in timescale")
        self._rides_to_timescale()
        self._logger.info("rides in timescale")

    def _stops_to_timescale(self):
        data_stops = pd.read_csv(DATA_DIR / "stops/Helsingin_ja_Espoon_kaupunkipyöräasemat_avoin.csv")
        data_stops = data_stops[~data_stops.isna().any(axis=1)]
        stops = list(zip(
            data_stops['Nimi'],
            data_stops['y'],
            data_stops['x']))
        try:
            self._timescale_connection.add_stops(stops)
        except Exception as e:
            self._logger.error(f"Error processing stops: {e}")

    def _rides_to_timescale(self):
        ride_list = []
        files = [f for f in (DATA_DIR / "results/").glob('**/*.csv') if f.is_file()]
        self._logger.info("Parallel processing rides...")

        with ProcessPoolExecutor() as executor:
            results = list(executor.map(process_rides, [str(file) for file in files]))
            for rides in results:
                ride_list.append(rides)
            executor.shutdown()    
        self._logger.info("Rides processed")

        self._logger.info("Inserting rides to timescale")
        i = 0
        for rides in ride_list:
            try:
                i += 1
                self._logger.info(f"Adding {len(rides)} rides")
                self._timescale_connection.add_rides(rides)
                self._logger.info(f"{i}/{len(ride_list)}")
            except Exception as e:
                self._logger.error(f"Error processing rides: {e}")
        self._logger.info("Finished inserting rides to timescale")
            

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


def process_rides(file_name):
    logger = logging.getLogger()
    print(f"adding rides from {file_name}")
    data_rides = pd.read_csv(DATA_DIR / "results/" / file_name)
    data_rides = data_rides[~data_rides.isna().any(axis=1)]

    rides = list(zip(
        data_rides['Departure'],
        data_rides['y'],
        data_rides['x'],
        data_rides['Rides_total'],
        data_rides['Rides_zerolength']
    ))

    print("completed rides from "+file_name)
    return rides
    

            
