### Exploratory data analysis
# intro-to-ds-2024 groupwork
# Miika Piiparinen, Hamid Aebadi, Maarja Mustimets

library(dplyr)
library(data.table)
library(tidytable)
library(lubridate)
library(ggplot2)
library(googleVis)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
folder_rides <- strsplit(folder, "intro-to-ds-2024/data") %>% paste0("data_too_big_for_git")


#* DATA IN ---------------------------------------------------------------------
#*--- Stations as reported by HSL --------------------
# HSL station data is specifically for 2018-2021
stations_HSL <- read.csv(paste0(folder, "/stops/Helsingin_ja_Espoon_kaupunkipyöräasemat_avoin.csv")) %>%
  mutate(across(all_of(c("FID","ID")), as.character))

#*--- Ride data -------------------
# Ride data is available for years 2016-2023, months April to October
rides <- readRDS(paste0(folder_rides, "/rides__2016_2023__processed.RDs"))
setDT(rides) # makes the data.frame a data.table, a faster structure

#*--- Ride data as stations-in-time -------------------
# Created in the code "data_transformation.R"
stations_intime <- readRDS(paste0(folder_rides, "/stations__2016_2023__1min.RDs"))
setDT(stations_intime)
# Stations with no coordinates: which years are they active in?
table(stations_intime[is.na(x),]$Departure.station.id, year(stations_intime[is.na(x),]$Departure), useNA="i")
  # but different stations in different years, but some in every year


#* DATA: RIDES -----------------------------------------------------------------
str(rides)
summary(rides)
table(weekdays(rides$Departure))

#*--- Speed -------------------
rides[!is.na(Duration) & !is.na(Covered.distance), ':='(Speed = Covered.distance/1000/(Duration/60/60))]
summary(rides$Speed)
  # Min.   1st Qu.    Median      Mean   3rd Qu.      Max.      NA's 
  #  0.0       9.1      11.4      16.7      13.4 1019462.1    225818 
# Some REALLY suspiciously high speeds (km/h) here
# Anything over 20 km/h seems too big for riding with these bikes in Helsinki
plot(density(log(rides$Speed), na.rm=T), xlim=c(0,10))
# Can't see the very high speeds on this plot, but I'll look into it


#*--- Distance -------------------
# What is the distribution in Covered.distance? 
# Let's to look at the distribution in kilometers:
summary(rides$Covered.distance/1000) # in kilometers
  # Min.  1st Qu.   Median     Mean  3rd Qu.     Max.     NA's 
  #0.000    1.031    1.794    2.311    2.985 3681.399     6188 

# How long are the longest rides? Are they realistic at all?
  # Someone could plausibly cover 15 km in an hour if riding all the time
rides_over15km <- rides %>% filter(!is.na(Covered.distance)) %>% 
  arrange(Covered.distance) %>% filter(Covered.distance/1000>15)
nrow(rides_over15km)/nrow(rides)*100 # 0.08% of rides
summary(rides_over15km$Speed)
  # Min.   1st Qu.    Median      Mean   3rd Qu.      Max.      NA's 
  #  0.0       5.4       8.3    7397.5      12.8 1019462.1        84 
plot(density(log(rides_over15km$Speed), na.rm=T)) # speeds that are too big definitely come out here

# How well is a ride's Covered.distance correlated with the as-the-eagle-flies 
  # distance between the departure and return station?
# ...



#*--- Duration -------------------
# Any rides longer than 24 hours are probably not "real", the line could probably even be drawn much earlier
# It is a known issue that parking can "fail", so the actual ride was much shorter than what "Duration" shows
# Maybe we can glean their actual duration from the distance covered.

# How many rides are over an hour in Duration? Over a day?
summary(rides$Duration/60) 
  # Min.  1st Qu.   Median     Mean  3rd Qu.     Max.     NA's 
  # 0.00     5.85     9.97    16.48    16.50 90027.65   209245 
# max is 90027.65 min ~ 62.5 days!

# Rides over an hour, which is the period of free riding
rides_overhour <- rides %>% arrange(Duration) %>% filter(Duration/60/60 > 1)
nrow(rides_overhour)/nrow(rides)*100 
  # roughly 1.2% of rides are over an hour
summary(rides_overhour$Covered.distance/1000)
  # Min.  1st Qu.   Median     Mean  3rd Qu.     Max.     NA's 
  #0.000    1.921    4.009    5.998    7.802 3681.391       23 
# A lot of realistic distances, but still some ridiculously big numbers
summary(rides_overhour$Speed)
  # Min.  1st Qu.   Median     Mean  3rd Qu.     Max.     NA's 
  #0.000    0.443    1.964    2.971    4.290 3359.426       23 
# Very low speeds, indicating staying put for a long time

rides_overday <- rides %>% arrange(Duration) %>% filter(Duration/60/60/24 > 1) 
nrow(rides_overday)/nrow(rides)*100
  # 0.05% of rides are over a day
summary(rides_overday$Covered.distance/1000)
  # Min.  1st Qu.   Median     Mean  3rd Qu.     Max.     NA's 
  #0.000    1.047    2.029    7.639    3.849 3681.009        5 
# Suspiciously, distances got shorter. Some of these bikes were probably left in once place for days on end.
summary(rides_overday$Speed)
  # Min.  1st Qu.   Median     Mean  3rd Qu.     Max.     NA's 
  #0.000  0.02270  0.04900  0.12869  0.09847 38.29124        5 
# Even lower speeds
hist(rides_overday$Duration/60/60/24, breaks=25)



#* ZERO-LENGTH RIDES -----------------------------------------------------------
# 1) Seeing really long-lasting rides with very small distances made me think about "illegitimate" rides.
# 2) It is known that many rides may be initiated just to be ended instantly
  # Often due to discovering some technical issue that makes riding the bike impossible
  # Also because of this, their Departure and Return station are the same
# How many such rides are there?
rides_samestation <- rides %>% filter(Departure.station.id==Return.station.id)
nrow(rides_samestation)/nrow(rides)*100
  # roughly 6.5% of rides have the same Departure and Return station
rides_samestation %>% summarise(Duration_min = Duration/60) %>% summary()
  # Overall short rides, but some big - could be those unsuccessful parkings or just roundtrips, unclear
rides_samestation %>% select(Covered.distance) %>% summary()
  # Mostly very small distances, median is 8 which is still equivalent to 
  # moving the bike just long enough to find a technical issue
# This seems like the makings of a detecting measure for "zero-length rides"

# Relations of this density distribution are easier to see on a logarithmic scale.
# Let's visualise the log-Covered.distance of same-station rides.
plot(density(log(rides_samestation$Covered.distance), na.rm=T), 
     main="Density of ln(Covered.distance) for rides that start and end in the same station")
lines(density(log(rides_samestation[rides_samestation$Duration<60, ]$Covered.distance), na.rm=T), col="Red")
  # For rides under a minute, the distances are very small, almost all under exp(4)~54.6 meters
  # Alternatively, plotting the line for under 2 minutes is already somewhat different
lines(density(log(rides_samestation[rides_samestation$Duration>=60*60, ]$Covered.distance), na.rm=T), col="Blue")
  # For rides over an hour, there are a very small number with a zero-like distance, 
  # but most have a big distance starting from exp(7)~1 kilometer -> implies a roundtrip
# lines(density(log(rides_samestation[
#   rides_samestation$Duration>=60 & rides_samestation$Duration<60*60, ]$Covered.distance), na.rm=T), col="Green")
  # For rides between a minute and an hour, 
  # most are rides starting from exp(6)~400 meters, which might be a reasonable roundtrip
legend("topright", legend=c("All rides","Rides under 60 sec", "Rides over 1 hour"),  
       fill = c("black","red","blue"))
# Based on the previous, I would consider a ride "zero-length", if it 
# has the same Departure and Return station and:
  # a) the ride is under 60 seconds long in Duration
  # b) the ride is under 50 meters long in Covered.distance



#*--- Indicator for zero-length rides -------------------
rides_samestation[, ':=' (Is_zerolength = ifelse(Duration<60 | Covered.distance<50, 1, 0))]
# Let's look at the resulting types
table(Is_zerolength=rides_samestation$Is_zerolength, useNA="i")
summary(rides_samestation[rides_samestation$Is_zerolength==0, c("Duration","Covered.distance","Speed")])
summary(rides_samestation[rides_samestation$Is_zerolength==1, c("Duration","Covered.distance","Speed")])
  # Yeah, pretty different "types" of rides



#* DATA: STATIONS-IN-TIME ------------------------------------------------------
# Zero-length ride indicator is already included
summary(stations_intime)

# for (i in c(2016:2016)) {
#   p1 <- ggplot()
#   p1 <- p1 + geom_line(mapping=aes(x=Departure, y=Rides_total), data=stations_intime[year(Departure) %in% i,])
#   p1
# }
stations_intime_day <- stations_intime %>%
  mutate(day = date(Departure)) %>% group_by(day) %>%
  summarise(N_zerolength = sum(Rides_zerolength))

AnnoTimeLine  <- gvisAnnotationChart(stations_intime_day, datevar="day",
                                       numvar="N_zerolength", 
                                       #titlevar="Title", #annotationvar="Departure",
                                       options=list(#displayAnnotations=TRUE,
                                                    legendPosition='newRow',
                                                    width=1200, height=600)
)
# Display chart
plot(AnnoTimeLine)
# Create Google Gadget
cat(createGoogleGadget(AnnoTimeLine), file="annotimeline.xml")

