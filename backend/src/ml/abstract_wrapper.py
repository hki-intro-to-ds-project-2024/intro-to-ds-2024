from src.db.timescale import TimescaleClient

from abc import ABC, abstractmethod

import logging

class AbstractWrapper(ABC):
    __logger: logging.Logger
    __timescale_connection: TimescaleClient
    __model: object

    def __init__(self, logger, timescale_connection):
        self.__logger = logger
        self.__timescale_connection = timescale_connection
        self.__model = self.__load_model

    @abstractmethod
    def _train_model(self):
        pass

    @abstractmethod
    def __load_model(self):
        pass

    @abstractmethod
    def predict(self, start_date, end_date):
        pass
