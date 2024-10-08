# intro-to-ds-2024 groupwork
# Miika Piiparinen, Hamid Aebadi, Maarja Mustimets

library(dplyr)
library(data.table)
library(tidytable)
library(ggplot2)
library(lubridate)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)


#* DATA IN ---------------------------------------------------------------------
#*--- Stop data -------------------
# Stop data is specifically for 2018-2021
stops <- read.csv(paste0(folder, "/stops/Helsingin_ja_Espoon_kaupunkipyöräasemat_avoin.csv"))

#*--- Ride data -------------------
# Ride data is available for years 2016-2023, months April to October
years <- c(2018) # "years" can be any subset of the years 2016-2023

ride_csvs <- list() # rides separated by year, by month (as they come in csv-s)
rides <- data.frame() # all rides will be put here

for (i in 1:length(years)) {
  folder_yeardata <- paste0(folder, "/rides_", years[i], "/")
  ride_csvs[[i]] <- lapply(paste0(folder_yeardata, list.files(folder_yeardata)), read.csv)
  for (j in ride_csvs[[i]]) {
    rides <- rbind(rides, j)
  }
}
summary(ride_csvs) # shows the number of years (number of rows) and number of months (length)
rm(ride_csvs) # this is not really necessary anymore

# Alternatively, data from all years 2016-2023 have already been put in here:
#rides <- readRDS(paste0(folder, "/ridedata__2016_2023.RDs")



#* PROCESSING ------------------------------------------------------------------
names(rides)[7:8] <- c("Covered.distance","Duration") # giving shorter, simpler names
setDT(rides) # makes the data.frame a data.table, a faster structure
summary(rides)
str(rides)

# Date and time wrangling:
rides[, c("Departure","Return")] <- rides[, lapply(.SD, as.POSIXct, format="%Y-%m-%dT%H:%M:%OS"), .SDcols=c("Departure","Return")]



#* EXPLORATORY DATA ANALYSIS ---------------------------------------------------
table(weekdays(rides$Departure))

# NB! Currently only based on rides from 2023

#*--- Distance -------------------
# What is the distribution in Covered.distance? 
# Let's to look at the distribution in kilometers:
summary(rides$Covered.distance/1000)
# Min.   1st Qu.    Median      Mean   3rd Qu.      Max.      NA's
# -4292.840     1.065     1.850     2.299     3.112  1184.750       830
  # Negative distances?
  # Also some ridiculously big numbers, have to look into that...
nrow(rides[rides$Covered.distance<0,]) # ok, just one
rides[rides$Covered.distance<0,] # it took 696 seconds ~ 11.6 minutes, 
  # so even the absolute value of the covered distance measure does not make any sense
  # I would currently assign it the value NA, as there are other such values in Covered.distance
rides[rides$Covered.distance<0, "Covered.distance"] <- NA

summary(rides$Covered.distance/1000)
#  Min.  1st Qu.   Median     Mean  3rd Qu.     Max.     NA's 
# 0.000    1.065    1.850    2.301    3.112 1184.750      831 

# How long are the longest rides? Are they realistic at all?
# Someone could plausibly cover 20 km in an hour if riding all the time
rides_over20km <- rides %>% filter(!is.na(Covered.distance)) %>% arrange(Covered.distance) %>% 
  summarise(Distance_km = Covered.distance/1000) %>% filter(Distance_km>20) # 546 only

# How well is a ride's Covered.distance correlated with the as-the-eagle-flies distance between the departure and return station?
# ...



#*--- Duration -------------------
# Any rides longer than 24 hours are probably not "real", the line could probably even be drawn much earlier
# It is a known issue that parking can "fail", so the actual ride was much shorter than what "Duration" shows
# Maybe we can glean their actual duration from the distance covered

# How many rides are over an hour in Duration? Over a day?
summary(rides$Duration/60) 
# Min.  1st Qu.   Median     Mean  3rd Qu.     Max. 
# 0.00     5.88    10.07    16.34    16.70 82139.58 
  # max is 82139.58 min ~ 1369 hours ~ 57 days!
n_rides_overhour <- rides %>% arrange(Duration) %>% summarise(Duration_days = Duration/60/60/24) %>% 
  filter(Duration_days>1/24) %>% nrow() 
  # 25589 rides over an hour
n_rides_overhour/nrow(rides)*100 
  # roughly 1% of rides are over an hour
rides_overday <- rides %>% arrange(Duration) %>% summarise(Duration_days = Duration/60/60/24) %>% 
  filter(Duration_days>1) 
nrow(rides_overday) 
  # 1115, very few rides over a day
hist(rides_overday$Duration_days, breaks=25)



#* ZERO-LENGTH RIDES -------------------
# It is known that many rides may be initiated just to be ended instantly
# Often due to discovering some technical issue that makes riding the bike impossible
# Also because of this, their Departure and Return station are the same
# How many such rides are there?
rides_samestation <- rides %>% filter(Departure.station.id==Return.station.id) # 126812
nrow(rides_samestation)/nrow(rides)*100
  # roughly 5% of rides have the same Departure and Return station
rides_samestation %>% summarise(Duration_min = Duration/60) %>% summary()
  # Overall much shorter rides, but some big - could be those unsuccessful parkings or just roundtrips, unclear
rides_samestation %>% select(Covered.distance) %>% summary()
  # Mostly very small distances, median is 10 which is still equivalent to moving the bike just long enough to find a technical issue
  # This seems like a better zero-length ride detecting measure

# Relations might be easier to see on a logarithmic scale?
# Let's visualise the log-Covered.distance of same-station rides.
plot(density(log(rides_samestation$Covered.distance), na.rm=T))
lines(density(log(rides_samestation[rides_samestation$Duration<60, ]$Covered.distance), na.rm=T), col="Red")
  # For rides under a minute, the distances are very small, almost all under exp(4)~54.6 meters
  # Under 2 minutes is already somewhat different
lines(density(log(rides_samestation[rides_samestation$Duration>=60*60, ]$Covered.distance), na.rm=T), col="Blue")
  # For rides over an hour, there are a very small number with a zero-like distance, 
  # but most have a big distance starting from exp(7)~1 kilometer -> implies a roundtrip
lines(density(log(rides_samestation[
  rides_samestation$Duration>=60 & rides_samestation$Duration<60*60, ]$Covered.distance), na.rm=T), col="Green")
  # For rides between a minute and an hour, 
  # most are rides starting from exp(6)~400 meters, which might be a reasonable roundtrip

# Based on the previous, I would consider a ride "zero-length", if it has the same Departure and Return station and:
  # a) the ride is up to one minute long in Duration
  # b) the ride is up to 50 meters long in Covered.distance



#*--- Indicator for zero-length rides -------------------
rides_samestation[, ':=' (Is_zerolength = ifelse(Duration<60 | Covered.distance<50, 1, 0))]
# Let's look at the resulting types
table(Is_zerolength=rides_samestation$Is_zerolength, useNA="i")
summary(rides_samestation[rides_samestation$Is_zerolength==0, c("Duration", "Covered.distance")])
summary(rides_samestation[rides_samestation$Is_zerolength==1, c("Duration", "Covered.distance")])
  # Yeah, pretty different "types" of rides



#*--- A table for stops in time with counts of zero-length rides -------------------
# Required variables: Stop id, coordinates, starting time of observed period, 
# total number of departures initiated in observed period, 
# number of "zero-length" rides initiated in observed period
rides_20180903_080000_15min <- rides[Departure>=as.POSIXct("2018-09-03 08:00:00") & 
                                       Departure<as.POSIXct("2018-09-03 08:15:00"),] %>%
  mutate(Is_zerolength = ifelse(Departure.station.id==Return.station.id & (Duration<60 | Covered.distance<50), 1, 0)) %>%
  group_by(Departure.station.id, Departure.station.name) %>%
  summarise(Rides_total = n(),
            Rides_zerolength = sum(Is_zerolength))

# Generalising a bit:
period_start <- as.POSIXct("2018-09-01 00:00:00")
period_end <- as.POSIXct("2018-09-30 23:59:59")
rides_period <- rides[Departure >= period_start & Departure <= period_end] %>%
  mutate(Is_zerolength = ifelse(Departure.station.id==Return.station.id & (Duration<60 | Covered.distance<50), 1, 0))

breaks <- seq(round(period_start,"hour"), round(period_end,"hour"), by="15 min")
rides_period$Departure.timeperiod <- cut(rides_period$Departure, breaks)

stations_period <- rides_period %>%
  # for grouping by minutes, Departure (that is the greatest possible accuracy);
  # for any other length of time, set up and use Departure.timeperiod:
  group_by(Departure, Departure.station.id, Departure.station.name) %>% 
  summarise(Rides_total = n(),
            Rides_zerolength = sum(Is_zerolength),) %>%
  left_join(stops[, c("ID", "x", "y")], by=c("Departure.station.id"="ID"))

write.csv(stations_period, paste0(folder, "/results/stations_201809_1min.csv")) # change file name accordingly
