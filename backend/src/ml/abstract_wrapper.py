from src.db.timescale import TimescaleClient

from abc import ABC, abstractmethod

import logging

class AbstractWrapper(ABC):
    _logger: logging.Logger
    _timescale_connection: TimescaleClient
    _model: object

    def __init__(self, logger, timescale_connection):
        self._logger = logger
        self._timescale_connection = timescale_connection
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
