from pathlib import Path
from enum import Enum

class Model(Enum):
    PROPHET = 1
    ARIMA = 2

DATA_DIR = Path(__file__).parent / ".." / ".." / "data"
FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend/dist/"
MIGRATIONS_DIR = Path(__file__).parent / "db/migrations"
MODELS_DIR = Path(__file__).parent / "ml/models"

DEVELOPMENT_ENV = True

TIMESCALE_CONN_STRING = "postgres://postgres:password@localhost/postgres"
INITIALIZE_DATABASE = False
TRAIN_MODEL = False

FILTERING_FRACTION = 0.1

MODEL_TO_USE = Model.ARIMA