from src.ml.abstract_wrapper import AbstractWrapper

from prophet import Prophet
from prophet.serialize import model_from_json

import pandas as pd
import numpy as np

class ProphetWrapper(AbstractWrapper):
    def __init__(self, logger, timescale_connection):
        super().__init__(logger, timescale_connection)

    def _train_model(self):
        df = self._timescale_connection.get_zero_rides()
        
        self._logger.info(f"Query complete: {df.head()}")

        df.rename(columns={'interval_start': 'ds', 'zero_rides': 'y'}, inplace=True)
        df['ds'] = df['ds'].dt.tz_localize(None)

        self._freq_encoding = df['stop_name'].value_counts() / len(df)
        df['stop_name_freq'] = df['stop_name'].map(self._freq_encoding)

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

        self._save_model(model, self._freq_encoding)

    def _load_model(self):
        super()._load_model()

    def _save_model(self, model, freq):
        super()._save_model(model, freq)

    def predict(self, start_date, end_date):
        df = self._timescale_connection.get_stop_names()

        station_names = df['stop_name'].unique()

        start_datetime = pd.to_datetime(start_date)
        end_datetime = pd.to_datetime(end_date)

        date_range = pd.date_range(start=start_datetime, end=end_datetime, freq='H')

        future = pd.DataFrame({
            'ds': pd.to_datetime(date_range.repeat(len(station_names))),
            'stop_name': station_names.tolist() * len(date_range)
        })

        future['stop_name_freq'] = future['stop_name'].map(self._freq_encoding)
        future['stop_name_freq'].fillna(self._freq_encoding.min(), inplace=True)

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