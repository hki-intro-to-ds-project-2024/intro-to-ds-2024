from src.db.timescale import TimescaleClient
from src.config import TRAIN_MODEL

from abc import ABC, abstractmethod

import logging

class AbstractWrapper(ABC):

    def __init__(self, logger, timescale_connection):
        self._freq_encoding = None
        self._logger = logger
        self._timescale_connection = timescale_connection
        if TRAIN_MODEL:
            self._train_model()
            self._logger.info("Model is trained")
        self._model = self._load_model

    @abstractmethod
    def _train_model(self):
        pass

    @abstractmethod
    def _load_model(self):
        pass

    @abstractmethod
    def predict(self, start_date, end_date):
        pass
