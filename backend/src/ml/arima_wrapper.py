from src.config import MODELS_DIR
from src.ml.abstract_wrapper import AbstractWrapper

import pandas as pd
import numpy as np
import joblib
from statsmodels.tsa.arima.model import ARIMA

class ArimaWrapper(AbstractWrapper):
    
    def __init__(self, logger, timescale_connection):
        super().__init__(logger, timescale_connection)

    def _train_model(self):
        df = self._timescale_connection.get_zero_rides()
        
        df.rename(columns={'interval_start': 'ds', 'zero_rides': 'y'}, inplace=True)
        df['ds'] = df['ds'].dt.tz_localize(None)

        self._freq_encoding = df['stop_name'].value_counts() / len(df)
        df['stop_name_freq'] = df['stop_name'].map(self._freq_encoding)

        self._logger.info("Training ARIMA model")

        model = ARIMA(df['y'].astype(float), order=(1, 1, 1), exog=df['stop_name_freq'].astype(float))
        fitted_model = model.fit()

        joblib.dump((fitted_model, self._freq_encoding), MODELS_DIR / "arima_model.pkl")
        self._logger.info("Model saved")

    def _load_model(self):
        super()._load_model()

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
        forecast = self._model.predict(start=len(df), end=len(df) + len(future) - 1, exog=future['stop_name_freq'])
        self._logger.info("Done!")

        station_forecast = pd.DataFrame({'ds': future['ds'], 'yhat': forecast})

        predictions = {}
        for station_id in station_names:
            station_predictions = station_forecast[future['stop_name'].values == station_id]
            predictions[station_id] = station_predictions

        return predictions

