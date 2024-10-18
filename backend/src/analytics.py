
from src.config import DATA_DIR, INITIALIZE_DATABASE, RIDE_BATCH_SIZE
from src.timescale import TimescaleClient
from random import randrange
from time import sleep
from prophet import Prophet
from prophet.serialize import model_from_json
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import pandas as pd
import logging

class Analytics:
    def __init__(self, logger):
        self._logger = logger
        self._timescale_connection = TimescaleClient(logger)
        self.__models = self._load_models()
        self._logger.info("Timescale connection initialized")
        if INITIALIZE_DATABASE:
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
        #
        files = [f for f in (DATA_DIR / "results/").glob('**/*.csv') if f.is_file()]
        self._logger.info("Parallel processing rides...")

        with ProcessPoolExecutor() as executor:
            results = list(executor.map(process_rides, [str(file) for file in files]))
            for rides in results:
                ride_list.append(rides)
            executor.shutdown()    
        self._logger.info("Rides processed")

        self._logger.info("Inserting rides to timescale in parallel...")

        with ThreadPoolExecutor() as executor:
            futures = []
            for ride_index, rides in enumerate(ride_list):
                futures.append(executor.submit(self._insert_rides_batch, rides, ride_index, len(ride_list), len(ride_list)))
            for future in futures:
                future.result()

        self._logger.info("Finished inserting rides to timescale")

    def _insert_rides_batch(self, rides, ride_index, total_rides, total_batches):
        """Helper function to insert a batch of rides"""
        try:
            self._logger.info(f"Inserting batch {ride_index + 1}/{total_batches} with {len(rides)} rides")
            self._timescale_connection.add_rides(rides)
        except Exception as e:
            self._logger.info(f"Error inserting batch {ride_index + 1}/{total_batches}: {e}")
        self._logger.info(f"completed batch {ride_index + 1}/{total_batches}")

    def _load_models(self):
        models = {}
        with open(DATA_DIR/"serialized_models.json", "r") as model_file:
            for item in model_file:
                item.rstrip("\n")
                data = item.split(";")
        
                if len(data) == 2:
                    id = data[0]
                    model = model_from_json(data[1])
                    models[id] = model
        return models
    
    def predict(self, start_date, end_date):
        predictions = {}
        # Convert the start and end strings to datetime format
        start_datetime = pd.to_datetime(start_date, format='%Y.%m.%d %H:%M:%S')
        end_datetime = pd.to_datetime(end_date, format='%Y.%m.%d %H:%M:%S')

        # Generate a date range with a frequency of 1 minute
        date_range = pd.date_range(start=start_datetime, end=end_datetime, freq='min')

        for station_id, model in self.__models.items():
            future = pd.DataFrame(date_range, columns=['ds'])
            predictions[station_id] = model.predict(future, include_history=False)[["ds", "yhat"]]

        return predictions


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
        data_rides['Rides_zerolength'],
        data_rides['Rides_zerolength_prop']
    ))

    print("completed rides from "+file_name)
    return rides