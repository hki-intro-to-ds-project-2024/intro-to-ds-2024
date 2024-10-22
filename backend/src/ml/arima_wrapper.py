from src.ml.abstract_wrapper import AbstractWrapper

import pandas as pd
import numpy as np

from math import floor
from statsmodels.tsa.arima.model import ARIMA

class ArimaWrapper(AbstractWrapper):
    
    def __init__(self, logger, timescale_connection):
        super().__init__(logger, timescale_connection)

    def _train_model(self):
        df = self._timescale_connection.get_zero_rides()
        
        df.rename(columns={'interval_start': 'ds', 'zero_rides': 'y'}, inplace=True)
        df['ds'] = df['ds'].dt.tz_localize(None)
        
        df['ds'] = df['ds'].dt.date

        self._freq_encoding = df['stop_name'].value_counts() / len(df)
        df['stop_name_freq'] = df['stop_name'].map(self._freq_encoding)
        
        df_daily = df.groupby(['ds', 'stop_name'], as_index=False).agg({'y': 'sum'})

        self._logger.info("Training ARIMA models for each station")

        self._models = {}
        for station_name, station_data in df_daily.groupby('stop_name'):
            station_data = station_data.sort_values('ds')
            endog = station_data['y'].astype(float)
            try:
                model = ARIMA(endog, order=(1, 1, 1))
                fitted_model = model.fit()
                self._models[station_name] = fitted_model
            except Exception as e:
                self._logger.error(f"Error training model for station {station_name}: {e}")
        
        self._save_model(self._models, self._freq_encoding)

    def _load_model(self):
        super()._load_model()

    def _save_model(self, models, freq_encoding):
        super()._save_model(models, freq_encoding)

    def predict(self, start_date, end_date):
        start_datetime = pd.to_datetime(start_date)
        end_datetime = pd.to_datetime(end_date)
        date_range = pd.date_range(start=start_datetime, end=end_datetime, freq='D')
        num_periods = len(date_range)

        predictions = {}
        self._logger.info(f"Starting prediction")
        for station_name, model in self._model.items():
            self._logger.info(f"Predicting for station: {station_name}")
            try:
                forecast = model.forecast(steps=num_periods)
                forecast = forecast.clip(lower=0)
                station_predictions = {
                    date.strftime('%Y-%m-%d'): floor(pred) 
                    for date, pred in zip(date_range, forecast)
                }
                predictions[station_name] = station_predictions
            except Exception as e:
                self._logger.info(f"Error predicting for station {station_name}: {e}")
                predictions[station_name] = {}
                
        return predictions
