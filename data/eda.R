### Exploratory data analysis
# intro-to-ds-2024 groupwork
# Miika Piiparinen, Hamid Aebadi, Maarja Mustimets

library(dplyr)
library(data.table)
library(tidytable)
library(lubridate) # for working with dates
library(ggplot2)
library(viridis) # for colours
library(ggmap)
library(googleVis)
#library(reshape)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
folder_rides <- strsplit(folder, "intro-to-ds-2024/data") %>% paste0("data_too_big_for_git")


#* DATA IN ---------------------------------------------------------------------
#*--- Stations as reported by HSL --------------------
# HSL station data is specifically for 2018-2021
stations_HSL <- read.csv(paste0(folder, "/stops/Helsingin_ja_Espoon_kaupunkipyöräasemat_avoin.csv")) %>%
  mutate(across(all_of(c("FID","ID")), as.character))

#*--- Stations from ride data -------------------
stations <- readRDS(paste0(folder_rides, "/stations_consolidated_fromRides.RDs")) %>% setDT()

#*--- Ride data -------------------
# Ride data is available for years 2016-2023, months April to October
rides <- readRDS(paste0(folder_rides, "/rides__2016_2023__processed.RDs"))
setDT(rides) # makes the data.frame a data.table, a faster structure

#*--- Ride data as stations-in-time -------------------
# Created in the code "data_transformation.R"

# stations_intime <- readRDS(paste0(folder_rides, "/stations_2016_2023__1min.RDs"))
# setDT(stations_intime)
# # Stations with no coordinates: which years are they active in?
# table(stations_intime[is.na(x),]$Departure.station.id, year(stations_intime[is.na(x),]$Departure), useNA="i")
#   # but different stations in different years, but some in every year

stations_intime <- setDT(readRDS(paste0(folder_rides, "/stations_consolidated__2016_2023__1min.RDs")))


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

# # Relations of this density distribution are easier to see on a logarithmic scale.
# # Let's visualise the log-Covered.distance of same-station rides.
# plot(density(log(rides_samestation$Covered.distance), na.rm=T), 
#      main="Density of ln(Covered.distance) for rides that start and end in the same station")
# lines(density(log(rides_samestation[rides_samestation$Duration<60, ]$Covered.distance), na.rm=T), col="Red")
#   # For rides under a minute, the distances are very small, almost all under exp(4)~54.6 meters
#   # Alternatively, plotting the line for under 2 minutes is already somewhat different
# lines(density(log(rides_samestation[rides_samestation$Duration>=60*60, ]$Covered.distance), na.rm=T), col="Blue")
#   # For rides over an hour, there are a very small number with a zero-like distance, 
#   # but most have a big distance starting from exp(7)~1 kilometer -> implies a roundtrip
# # lines(density(log(rides_samestation[
# #   rides_samestation$Duration>=60 & rides_samestation$Duration<60*60, ]$Covered.distance), na.rm=T), col="Green")
#   # For rides between a minute and an hour, 
#   # most are rides starting from exp(6)~400 meters, which might be a reasonable roundtrip
# legend("topright", legend=c("All rides","Rides under 60 sec", "Rides over 1 hour"),  
#        fill = c("black","red","blue"))
# # Based on the previous, I would consider a ride "zero-length", if it 
# # has the same Departure and Return station and:
#   # a) the ride is under 60 seconds long in Duration
#   # b) the ride is under 50 meters long in Covered.distance

ticks_metric = c(paste0(c(1,12,148), "m"), paste0(c("1.8","22","268","3269"),"km"))

# Same plot with all the accoutrements:
plot(density(log(rides_samestation$Covered.distance), na.rm=T),
     xlim=c(-0.5, 15.5), xaxt = "n", ylim=c(0, 0.2),
     xlab="Covered.distance", ylab="Proportion of rides",
     main="Density of ln(Covered.distance) for rides that start and end in the same station")
abline(v=seq(0,15,2.5), col="grey", lty=1) # background lines
lines(density(log(rides_samestation[rides_samestation$Duration<60, ]$Covered.distance), na.rm=T), col="Red")
lines(density(log(rides_samestation[rides_samestation$Duration>=60*60, ]$Covered.distance), na.rm=T), col="Blue")
legend("topright", legend=c("All rides","Rides under 60 sec", "Rides over 1 hour"),  
       fill = c("black","red","blue"))
abline(v=log(50), col="black", lty="dashed") # line for 50m, which is our chosen cutoff point
axis(1, at = c(seq(0,15,2.5), log(50)), labels = c(ticks_metric, "50m")) # ticks in metric

# Progression of density over years:
plot(density(log(rides_samestation[year(Departure)==2016,]$Covered.distance), na.rm=T), 
     lwd=2, col=colours[1],
     xlim=c(-0.5, 15.5), xaxt = "n", ylim=c(0, 0.2),
     xlab="Covered.distance", ylab="Proportion of rides",
     main="Rides with the same start and end station in 2016-2023")
abline(v=seq(0,15,2.5), col="grey", lty=1) # background lines
colours=rev(viridis(8)) # generates 8 colours at equal distance
for (i in 1:length(2017:2023)) {
  data <- rides_samestation %>% filter(year(Departure) %in% c(2016:2023)[i+1])
  print(nrow(data))
  lines(density(log(data$Covered.distance), na.rm=T), col=colours[i+1], lwd=2)
}
legend("topright", legend=c(2016:2023), fill = colours)
abline(v=log(50), col="black", lty="dashed") # line for 50m, which is our chosen cutoff point
abline(v=log(50), col="black", lty="dashed", lwd=1) # line for 50m, which is our chosen cutoff point
axis(1, at = c(seq(0,15,2.5), log(50)), labels = c(ticks_metric, "50m"), lwd=1) # ticks in metric


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

#*--- Stations with most 0L-rides ----------------------------------------------
top_nr <- 30
stations_intime_year <- stations_intime[!is.na(x)] %>%
  mutate(year = year(Departure)) %>% 
  group_by(x, y, year) %>%
  summarise(N_zerolength = sum(Rides_zerolength),
            N_total = sum(Rides_total)) %>%
  mutate(prop_zerolength = round(N_zerolength/N_total,3))
summary(stations_intime_year)
# If the only ride were 0-L, then the proportion would be 1 -> removing stations with super low riderships
top_zerolengthrides <- stations_intime_year %>%
  filter(N_total >= 100) %>%
  ungroup() %>% group_by(year) %>% top_n(top_nr, wt=prop_zerolength) %>%
  left_join(stations_HSL[, c("x","y","Name","Kapasiteet")], by=c("x","y"))

tmp <- top_zerolengthrides %>% group_by(x, y) %>%
  summarise(N_zerolength = sum(N_zerolength),
            N_total = sum(N_total)) %>%
  mutate(prop_zerolength = round(N_zerolength/N_total,3))

#- - - Map:
mapgilbert <- get_map(location = c(mean(tmp$x), mean(tmp$y)),
                      maptype="roadmap",
                      scale = "auto", zoom = 11)
ggmap(mapgilbert) +
  geom_point(data = tmp, aes(x = x, y = y, fill = "red", size = N_zerolength, alpha = 0.96), shape = 21) +
  guides(fill=FALSE, alpha=FALSE, size=FALSE)

#- - - For centre of Helsinki:
map_centre <- get_map(location = c(24.94, 60.17), # roughly downtown
                      maptype="roadmap",
                      scale = "auto", zoom = 13)
ggmap(map_centre) +
  geom_point(data = tmp, aes(x = x, y = y, fill = "red", size = N_zerolength, alpha = 0.96), shape = 21) +
  guides(fill=FALSE, alpha=FALSE, size=FALSE)



#*------ Top stations across all years (in top 30 by proportion on 3+ years) ----
top_alltime <- top_zerolengthrides %>% group_by(x, y) %>%
  summarise(N_years = n(), N_zerolength = sum(N_zerolength)) %>% 
  filter(N_years >= 3) %>%
  left_join(stations_HSL[, c("x","y","Name","Kapasiteet")], by=c("x","y"))
top_alltime_yearly <- stations_intime_year %>% 
  filter(x %in% top_alltime$x & y %in% top_alltime$y) %>% 
  select(-N_zerolength, -N_total) %>%
    dcast(x+y ~ year, value.var = "prop_zerolength") %>%
  left_join(top_alltime, by=c("x","y"))

mapgilbert <- get_map(location = c(lon = mean(top_alltime$x), lat = mean(top_alltime$y)),
                      maptype="roadmap",
                      scale = "auto", zoom = 11)
ggmap(mapgilbert) +
  geom_point(data = top_alltime, aes(x = x, y = y, fill = "red", size = N_zerolength, alpha = 0.96), shape = 21) +
  guides(fill=FALSE, alpha=FALSE, size=FALSE)

#- - - For centre of Helsinki:
ggmap(map_centre) +
  geom_point(data = top_alltime, aes(x = x, y = y, fill = "red", size = N_zerolength), shape = 21) +
  guides(fill=FALSE, alpha=FALSE, size=FALSE)



#*--- Plot visualising number of 0L-rides in time ------------------------------
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

