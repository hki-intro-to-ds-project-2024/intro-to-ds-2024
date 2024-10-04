# intro-to-ds-2024
A project where we aim to provide maintanance suggestions on the bikestops of the city of Helsinki. Uses a flask backend with a timescale database and typescript/react frontend. Analytics by Maarja Mustimets done with R.

## How to run
- Have docker installed for easy timescale db 
- Have python installed with poetry
- Have some version of npm installed
- create a .env file into the frontend directory and add your google api key

`GOOGLE_MAPS_API_KEY="{your key}"`
- run `buildrun.sh`
- go to the url given to you by flask

## Resources
- [Canvas](https://docs.google.com/document/d/1QWejvSXaniifYWSfj8oD7vjKZFbPcpI-s3F1d9oqQH8/edit?usp=sharing)
- [Bike ride data 2016-2024](https://hri.fi/data/en_GB/dataset/helsingin-ja-espoon-kaupunkipyorilla-ajatut-matkat)
- [Bike station data 2018-2021](https://hri.fi/data/en_GB/dataset/hsl-n-kaupunkipyoraasemat)
