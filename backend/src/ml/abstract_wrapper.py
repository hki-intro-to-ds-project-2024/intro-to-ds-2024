from src.db.timescale import TimescaleClient
from src.config import TRAIN_MODEL, MODEL_TO_USE, MODELS_DIR

from abc import ABC, abstractmethod

import logging
import joblib

class AbstractWrapper(ABC):

    def __init__(self, logger, timescale_connection):
        self._freq_encoding = None
        self._logger = logger
        self._timescale_connection = timescale_connection
        if TRAIN_MODEL:
            self._train_model()
            self._logger.info("Model is trained")
        self._load_model()

    @abstractmethod
    def _train_model(self):
        pass

    @abstractmethod
    def _load_model(self):
        self._logger.info(f"Loading Model {MODELS_DIR / f"{(MODEL_TO_USE.name).lower()}_model.pkl"}")
        self._model, self._freq_encoding = joblib.load(MODELS_DIR / f"{(MODEL_TO_USE.name).lower()}_model.pkl")
        self._logger.info("Model loaded")

    @abstractmethod
    def _save_model(self, model, encoding):
        self._logger.info("Saving Model")
        joblib.dump((model, encoding), MODELS_DIR / f"{(MODEL_TO_USE.name).lower()}_model.pkl")
        self._logger.info("Model saved")

    @abstractmethod
    def predict(self, start_date, end_date):
        pass
