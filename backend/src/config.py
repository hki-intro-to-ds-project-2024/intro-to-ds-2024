from pathlib import Path

DATA_DIR = Path(__file__).parent / ".." / ".." / "data"
FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend/dist/"
MIGRATIONS_DIR = Path(__file__).parent / "migrations"

DEVELOPMENT_ENV = True

TIMESCALE_CONN_STRING = "postgres://postgres:password@localhost/postgres"
INITIALIZE_DATABASE = True

RIDE_BATCH_SIZE = 1000
