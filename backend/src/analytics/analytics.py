from src.config import DATA_DIR, INITIALIZE_DATABASE, FILTERING_FRACTION, MODEL_TO_USE, Model
from src.db.timescale import TimescaleClient
from src.ml.prophet_wrapper import ProphetWrapper
from src.ml.arima_wrapper import ArimaWrapper

from random import randrange
from time import sleep
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import pandas as pd
import logging

class Analytics:
    def __init__(self, logger):
        self.__logger = logger
        self.__timescale_connection = TimescaleClient(logger)
        self.__logger.info("Timescale connection initialized")
        if INITIALIZE_DATABASE:
            self.__timescale_connection.apply_schema("zero_rides.sql")
            self.__stops_to_timescale()
            self.__logger.info("stops in timescale")
            self.__rides_to_timescale()
            self.__logger.info("rides in timescale")
        self.__logger.info(f"Using model {MODEL_TO_USE.name}")
        if MODEL_TO_USE == Model.PROPHET:
            self.__model = ProphetWrapper(logger.getChild(MODEL_TO_USE.name),
                                            self.__timescale_connection)
        if MODEL_TO_USE == Model.ARIMA:
            self.__model = ArimaWrapper(logger.getChild(MODEL_TO_USE.name),
                                            self.__timescale_connection)
        self.__logger.info("Prediction:" + str(self.__model.predict('2021-01-02', '2021-01-03')))

    def predict(self, start_date, end_date):
        return self.__model.predict(start_date, end_date)

    def __stops_to_timescale(self):
        data_stops = pd.read_csv(DATA_DIR / "stops/Helsingin_ja_Espoon_kaupunkipyöräasemat_avoin.csv")
        data_stops = data_stops[~data_stops.isna().any(axis=1)]
        stops = list(zip(
            data_stops['Nimi'],
            data_stops['y'],
            data_stops['x']))
        try:
            self.__timescale_connection.add_stops(stops)
        except Exception as e:
            self.__logger.error(f"Error processing stops: {e}")

    def __rides_to_timescale(self):
        ride_list = []
        files = [f for f in (DATA_DIR / "results/stations__2016_2023__1min/").glob('**/*.csv') if f.is_file()]
        self.__logger.info("Parallel processing rides...")

        with ProcessPoolExecutor() as executor:
            results = list(executor.map(process_rides, [str(file) for file in files]))
            for rides in results:
                ride_list.append(rides)
            executor.shutdown()    
        self.__logger.info("Rides processed")

        self.__logger.info("Inserting rides to timescale in parallel...")

        with ThreadPoolExecutor() as executor:
            futures = []
            for ride_index, rides in enumerate(ride_list):
                futures.append(executor.submit(self.__insert_rides_batch, rides, ride_index, len(ride_list), len(ride_list)))
            for future in futures:
                future.result()

        self.__logger.info("Finished inserting rides to timescale")

    def __insert_rides_batch(self, rides, ride_index, total_rides, total_batches):
        """Helper function to insert a batch of rides"""
        try:
            self.__logger.info(f"Inserting batch {ride_index + 1}/{total_batches} with {len(rides)} rides")
            self.__timescale_connection.add_rides(rides)
        except Exception as e:
            self.__logger.info(f"Error inserting batch {ride_index + 1}/{total_batches}: {e}")
        self.__logger.info(f"completed batch {ride_index + 1}/{total_batches}")

    def __load_models(self):
        models = {}
        with open("serialized_models.json", "r") as model_file:
            for item in model_file:
                item.rstrip("\n")
                data = item.split(";")
        
                if len(data) == 2:
                    id = data[0]
                    model = model_from_json(data[1])
                    models[id] = model
        return models
    
    def predict(self, start_date, end_date):
        return self.__model.predict(start_date, end_date)

    def get_nodes_json(self, time_start, time_end, zero_rides, proportion):
        node_list = self.__timescale_connection.get_nodes(time_start, time_end, zero_rides, proportion)
        nodes = []
        for i, node in enumerate(node_list):
            nodes.append({
                'position': {'lat': node[0], 'lng': node[1]},
                'id': i,
                'type': 'pin',
                'zIndex': 100
            })
        return nodes

    def get_predictions_json(self, time_start, time_end, zero_rides):
        coord_dict = self.__timescale_connection.get_coord_dict()
        node_dict = self.predict(time_start, time_end)
        self.__logger.info(node_dict)
        predictions = []
        for i, node in enumerate(node_dict):
            lat, lng = coord_dict[node]
            zero_rides_pred = 0
            for date in node_dict[node]:
                zero_rides_pred += int(node_dict[node][date])
            if zero_rides_pred >= int(zero_rides):
                predictions.append({
                    'position': {'lat': lat, 'lng': lng},
                    'rides': int(zero_rides_pred),
                    'id': i + 500,
                    'type': 'html',
                    'zIndex': 99
                })
        return predictions

def process_rides(file_name):
    logger = logging.getLogger()
    print(f"adding rides from {file_name}, filtering", FILTERING_FRACTION*100, "%")
    data_rides = pd.read_csv(DATA_DIR / "results/" / file_name).sample(frac=FILTERING_FRACTION)
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