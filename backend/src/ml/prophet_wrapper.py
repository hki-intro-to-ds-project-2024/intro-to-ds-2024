from src.config import TRAIN_MODEL, MODELS_DIR
from src.ml.abstract_wrapper import AbstractWrapper

from prophet import Prophet
from prophet.serialize import model_from_json
from sqlalchemy import create_engine

import pandas as pd
import numpy as np
import joblib

class ProphetWrapper(AbstractWrapper):
    def __init__(self, logger, timescale_connection):
        self._logger = logger
        self._timescale_connection = timescale_connection
        self.freq_encoding = None
        if TRAIN_MODEL:
            self._train_model()
            self._logger.info("Model is trained")
        self._model = self._load_model()
        self._logger.info("Prophet initialized")
        self._logger.info("Prediction:" + str(self.predict('2023-01-01', '2023-01-02')))

    def _train_model(self):
        engine = create_engine('postgresql://postgres:password@localhost/postgres')

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

        df = pd.read_sql(query, engine)
        
        self._logger.info(f"Query complete: {df.head()}")

        df.rename(columns={'interval_start': 'ds', 'zero_rides': 'y'}, inplace=True)
        df['ds'] = df['ds'].dt.tz_localize(None)

        self.freq_encoding = df['stop_name'].value_counts() / len(df)
        df['stop_name_freq'] = df['stop_name'].map(self.freq_encoding)

        self._logger.info(df.head(20))
        self._logger.info("Frequency encoding complete")
        self._logger.info("Adding regressors")

        model = Prophet()
        model.add_regressor('stop_name_freq')

        self._logger.info("Regressors complete")
        self._logger.info("Fitting Model")

        model.fit(df[['ds', 'y', 'stop_name_freq']])

        self._logger.info("Fitting complete")
        self._logger.info("Saving Model")

        joblib.dump((model, self.freq_encoding), MODELS_DIR / "prophet_model.pkl")
        self._logger.info("Model saved")

    def _load_model(self):
        self._logger.info("Loading Model")
        self._model, self.freq_encoding = joblib.load(MODELS_DIR / "prophet_model.pkl")
        self._logger.info("Model loaded")
        return self._model

    def predict(self, start_date, end_date):
        engine = create_engine('postgresql://postgres:password@localhost/postgres')
        query = "SELECT DISTINCT stop_name FROM stops"
        df = pd.read_sql(query, engine)

        station_names = df['stop_name'].unique()

        start_datetime = pd.to_datetime(start_date)
        end_datetime = pd.to_datetime(end_date)

        date_range = pd.date_range(start=start_datetime, end=end_datetime, freq='H')

        future = pd.DataFrame({
            'ds': pd.to_datetime(date_range.repeat(len(station_names))),
            'stop_name': station_names.tolist() * len(date_range)
        })

        future['stop_name_freq'] = future['stop_name'].map(self.freq_encoding)
        future['stop_name_freq'].fillna(self.freq_encoding.min(), inplace=True)

        future['ds'] = future['ds'].dt.tz_localize(None)

        self._logger.info("Predicting!")
        forecast = self._model.predict(future[['ds', 'stop_name_freq']])
        self._logger.info("Done!")
        forecast['stop_name'] = future['stop_name']

        predictions = {}
        for station_id in station_names:
            station_forecast = forecast[forecast['stop_name'] == station_id][['ds', 'yhat']]
            predictions[station_id] = station_forecast

        return predictions