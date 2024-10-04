#!/bin/bash

docker pull timescale/timescaledb-ha:pg16
docker run -d --name timescaledb -p 5432:5432 -e POSTGRES_PASSWORD=password timescale/timescaledb-ha:pg16
git pull --rebase --autostash

cd frontend
npm install
npm run build

cd ../backend
poetry install
poetry run python main.py
