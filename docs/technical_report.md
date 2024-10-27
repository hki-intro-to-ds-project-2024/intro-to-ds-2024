# Technical Report

This report details the chronological-, technical- and practical elements of what ended up becoming the "Biketainer" project.

## Project Chronology

The whole project processing happened in 3 main phases.

**Brainstorming Phase (2 weeks)**: Thanks to the intiative taken by Maarja, we reached a relatively swift consensus of working with Open Bicycle Data. We did juggle the idea of doing something with medical data, but deemed the data there to require too much subject matter expertise to work with. We were originally going to attempt working with equivalent data from Estonia, but chose against it, as the Helsinki bicycle data was more abundant. The `data/data_info.md` defines the data we ended up using, but it also defined traffic data which we thought could provide for interesting insights. However, this data was scrapped mostly due to time constraints.

Miika started building the backbone of the application at this point, implementing a trivial flask api and some frontend components, including tapping into the Google Maps API to render the map of Helsinki. Some time was spent between Miika and Maarja for skills exchange when it comes to software development conventions in Python, as the latter was not yet experienced in the topic. Later, Maarja would migrate to mostly do analytics in the data directory with R.

**Technical Fine-tuning Phase (3 weeks)**:
In this phase of the project we knew we were locked-in to the bicycle data. Now we needed to defined our technical solution in a more concrete way. Initially we thought "graph optimization" combined with some vague hand-waving was going give us the keys to the kingdom, but later we arrived to a more technically sound and interesting solution. The main limitation in the graph optimization solution was the lack of data and clarity, which was not the case in the actual solution we decided to implement.

As stated, the general prospect initially was optimizing the network of bikes and defining the edges of the network, both in terms of physical distance and flow. We wanted to use a Ford-Fulkerson-esque algorithmic solution initially, seeking to chart out and optimize flow's in the graph, but the precise form of this was unclear for a lengthy amount of time. In the end, such a solution was scrapped in favour of a predictive time-series approach. 

The team drifted into a time-series based approach in a discussion forum around the middle of the project. Maarja had done thorough EDA and found that events the team would later come to call "zero-rides" occur, where a person seemingly takes a bicycle out and returns it back in a very short timeframe. She had considered that these events could be related to – at least partially – broken bicycles, especially if they occur in a quick succession. Miika had been considering time-series based solutions for his personal- and work-related projects, and wanted to implement a predictive solution as well as a Timescale database instance that'd be tied to the project.

Thus, the final formulation of the project revolved around predicting zero-ride events, and hence giving the customer insights on where potential breakages may occur in the future. During this time, Miika was finishing up the node visualization portion in the frontend, and had started setting up the timescale database. Hamid had been given the responsibility to implement the machine learning solution known as Prophet by Miika, and he formulated the idea of using multiple models for prediction. However, his prophet-based solution was scrapped due to testing done by Miika, where the numbers produced by Prophet were nonsensical compared to the alternative ARIMA-solution. 

 **Polishing Phase (2 weeks)**: 
The final weeks of the project were mostly spent on the machine learning solution, as well as tying the moving parts together in a frenzy.


## Technical Solutions

### Software

- The backend of the project follows a very basic object-oriented paradigm. An abstract wrapper class for machine learning solutions was implemented, which means to enhance development velocity of the software in the future by allowing multiple machine learning models to interface with the product in a homogenous fashion. A restful flask api is used for the backend, from which the frontend fetches JSON packets using GET-requests. The packets were not defined very rigorously, f.e. using an open-api spec or equivalent. They mostly contain coordinate data for existing or predicted nodes. The application interfaces with an Analytics class, which talks to both the machine learning models and the timescale database.

- The timescale database is interfaced via a TimescaleClient class. It's a postgres-native solution where timestamps are converted to an index of a hypertable that allows for swift queries and aggregation of mass-amounts of timeseries data. The database runs on a simple docker container. To note, the initial insert of data into the database is parallelized for speed. The analytics class also utilizes some parallelism where applicable. The queries ended up being very fast, with millions of rows of time-series data being fetched and aggregated in seconds.

- The frontend of the project is a simple React-based application that uses the Google Maps API to render geographical data. Due to a lack of a strong frontend engineer in the team, the GUI portion is very much an MVP, adhering to no strong design principles worth talking about. 

- The machine learning solution Prophet was initially going to be used, but it gave bizarre predicitions as it's not very useful in predicting discrete values on such a small range (really the realistic prediction-space is [1..10]). ARIMA worked much better for this, and via rounding out the numbers, the solution could land some degree of accuracy in it's predictions. Sadly, the fine-tuning of the solution must be left for future development, if applicable. 

### Statistics and EDA


#### Challenges and improvements
During the project timeline we faced many challenges. Technical, theoretical,
deadline and other kinds of challenges that are typical in group projects.There were some
workload imbalance between team members. 

The idea-establishment was one of the most time-consuming issue. At the first, the initial idea
suposed to be clear and practical but later we realized that we cannot get out of it too much
usefule information so we had to try another ideas.

The most important thing is that we didn't give up and fortunately we managed to
get something useful as outcome. 