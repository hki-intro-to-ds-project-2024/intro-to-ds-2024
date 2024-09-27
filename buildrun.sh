#!/bin/bash

git pull --rebase --autostash

cd frontend
npm install
npm run build

cd ../backend
poetry install
poetry run python main.py
