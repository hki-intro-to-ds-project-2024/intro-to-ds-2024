import pandas as pd
from prophet import Prophet
from prophet.serialize import model_to_json
import json

data = pd.read_csv("stations__2016_2023__1min.csv", low_memory=False)
data.drop(columns="y", inplace=True)
data.rename(columns={"Departure": "ds", "Rides_zerolength":"y"}, errors="raise", inplace=True)
data['ds'] = pd.to_datetime(data['ds'])

#data = data[data['ds'].dt.year != 2016]
#data = data[data['ds'].dt.year != 2017]
#data = data[data['ds'].dt.year != 2018]

groups = data.groupby("Departure.station.id")[["ds", "y"]]
print("Group lentgh")
print(len(groups))
models = {}

counter = 0

print("Start training")
for key, data in groups:
    model = Prophet()
    model.fit(data)
    counter += 1
    print(f"{counter} stations fitted till now")
    print("Write to the file")
    with open("serialized_models.json", "a") as fout:
        fout.write(f"{key};{model_to_json(model)}\n")
    print("Succeffully added to the file")

#write dict into a file

print("Training ended successfully")
with open("serialized_models.json", "a") as fout:
    fout.write(json.dumps(models))
