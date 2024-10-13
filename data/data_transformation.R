### Creating the csv to be used by the python application
# intro-to-ds-2024 groupwork
# Miika Piiparinen, Hamid Aebadi, Maarja Mustimets

library(dplyr)
library(data.table)
library(tidytable)
library(lubridate)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
folder_bigdata <- strsplit(folder, "intro-to-ds-2024/data") %>% paste0("data_too_big_for_git")


#* DATA IN ---------------------------------------------------------------------
#*--- Rides --------------------
# Use when reading in the rides for the first time: # fix this
# years <- c(2016:2023)
# ride_csvs <- list() # rides separated by year, by month (as they come in csv-s)
# rides <- data.frame() # all rides will be put here
# for (i in 1:length(years)) {
#   folder_yeardata <- paste0(folder_bigdata, "/Data from HSL/rides_", years[i], "/")
#   ride_csvs[[i]] <- lapply(paste0(folder_yeardata, list.files(folder_yeardata)), read.csv)
#   for (j in ride_csvs[[i]]) {
#     rides <- rbind(rides, j)
#   }
# }
# rm(ride_csvs)
# saveRDS(rides, paste0(folder_bigdata, "/rides__2016_2023.RDs"))

# Read in the premade RDs:
rides <- readRDS(paste0(folder_bigdata, "/rides__2016_2023.RDs"))


#*--- Stations as reported by HSL --------------------
# HSL station data is specifically for 2018-2021
stations_HSL <- read.csv(paste0(folder, "/stops/Helsingin_ja_Espoon_kaupunkipyöräasemat_avoin.csv")) %>%
  mutate(across(all_of(c("FID","ID")), as.character))
summary(stations_HSL) # ok, no NAs


#* PROCESSING ------------------------------------------------------------------
#*--- Processing ride data --------------------
setDT(rides)
names(rides)[7:8] <- c("Covered.distance","Duration") # giving shorter, simpler names

# Date and time wrangling:
rides[, c("Departure","Return")] <- 
  rides[, lapply(.SD, as.POSIXct, format="%Y-%m-%dT%H:%M:%OS"), .SDcols=c("Departure","Return")]

# Correction(s):
# I found one ride that had a nonsensical covered distance, imputing:
rides[rides$Covered.distance<0, "Covered.distance"] <- NA

# Are there rides with an unclear Departure or Return station?
tmp <- rides[is.na(Departure.station.id) | is.na(Return.station.id),] # 984 rides
table(`Duration>0`=tmp$Duration>0, `Covered.distance>0`=tmp$Covered.distance>0, useNA="i")
  # a good third are "zero-length" rides, I will impute their Departure and Return station to be identical:
rides[!Departure.station.id %in% c(NA,""," ") & is.na(Return.station.id) &
        (Duration<60 | Covered.distance<50), ':='(Return.station.id = Departure.station.id)]
rides[is.na(Departure.station.id) & !Return.station.id %in% c(NA,""," ") &
        (Duration<60 | Covered.distance<50), ':='(Departure.station.id = Return.station.id)]
# Check again:
tmp <- rides[is.na(Departure.station.id) | is.na(Return.station.id),] # 109
  # These do not seem to be usable for the purposes of station-in-time data
  # Nor much else really, removing them:
rides <- rides[!is.na(Departure.station.id) & !is.na(Return.station.id),]


#*------ Saving ride data --------------------
saveRDS(rides, paste0(folder_bigdata, "/rides__2016_2023__processed.RDs"))
#rides <- readRDS(paste0(folder_bigdata, "/rides__2016_2023__processed.RDs"))



#*--- Processing station data --------------------
# Trimming whitespace:
rides[, c("Departure.station.name","Return.station.name")] <- 
  rides[, lapply(.SD, trimws), .SDcols=c("Departure.station.name","Return.station.name")]

# Checking that there are no two different station IDs with the same name in the HSL data:
stations_HSL %>% select(FID) %>% unique() %>% nrow() # 457
stations_HSL %>% select(Nimi) %>% unique() %>% nrow() # 456
stations_HSL %>% group_by(Nimi) %>% summarise(Count = n()) %>% filter(Count>1) %>% left_join(stations_HSL) %>% View()
  # Ok, 1 exception! Haukilahdenkatu has two different locations. To prevent further confusion,
  # I will modify the data in one of the cases:
rides[Departure.station.id==583, ':=' (Departure.station.name = "Haukilahdenkatu II")]

# There are IRL stations that have have different IDs but same name through time, 
  # as well as IRL station that have had different names but same ID through time.
# We assume that for some historical reasons, some stations have had to be reestablished with a new name, 
  # but the location has essentially stayed the same.
# We will keep the unique IDs; the names may help with imputing coordinates.

# Creating station data from ride data:
stations <- rides %>%
  group_by(Departure.station.id, Departure.station.name) %>% 
  summarise(Rides_total = n()) %>% ungroup() %>%
  mutate(Departure.station.name = trimws(Departure.station.name)) %>%
  left_join(stations_HSL[, c("ID", "x", "y")], by=c("Departure.station.id"="ID"))

# It is known that station with id 997 causes issues with varying coordinates:
table(rides[Departure.station.id==997, Departure.station.name], useNA="i")
  # It seems to be the bike workshop, we will remove those rides in the next step

# Removing stations with "test" or "workshop" in the name, as those are not available to the public:
test_stations <- rides[, "Departure.station.name"] %>% unique() %>%
  filter(grepl("Workshop", Departure.station.name) | grepl("workshop", Departure.station.name) |
           grepl("Test", Departure.station.name) | grepl("test", Departure.station.name) |
           grepl("Production", Departure.station.name)) %>% unlist()
nrow(rides[Departure.station.name %in% test_stations,]) # 1258 rides
stations <- stations[(!Departure.station.name %in% test_stations) & (!Departure.station.id %in% 997),]
rm(test_stations)

# Removing stations with only one ride departing from them:
table(stations$Rides_total==1, useNA="i") # 12 stations with only one departure
stations <- stations[Rides_total>1,]


#*------ Checking for missing station coordinates --------------------
table(is.na(stations$x), useNA="i")
  # 165 ~ 25% of stations have no coordinates given in the stations_HSL dataset
stations %>% mutate(Coords_NA = is.na(x)) %>% group_by(Coords_NA) %>% 
  summarise(Rides_total = sum(Rides_total)/sum(stations$Rides_total)*100) 
  # however, only 3.53% of rides originate from Stations with no coordinates

stations_no_coords <- stations %>% filter(is.na(x))
table(stations_no_coords$Departure.station.name %in% stations_HSL$Nimi, useNA="i")
  # Although there were no coordinates available by ID (in a previous step),
  # Most of the stations with no coordinates share a name with a station in station_HSL with coordinates
# Assigning coordinates by station name:
stations <- left_join(stations, stations_HSL[, c("Nimi","x","y")], 
                      by=c("Departure.station.name"="Nimi"), suffix=c("","_byName")) %>%
  mutate(x = case_when(!is.na(x) ~ x,
                       !is.na(x_byName) ~ x_byName,
                       TRUE ~ NA),
         y = case_when(!is.na(y) ~ y,
                       !is.na(y_byName) ~ y_byName,
                       TRUE ~ NA)) %>% 
  select(-x_byName, -y_byName)
stations_no_coords <- stations %>% filter(is.na(x)) # 19 stations remaining
stations %>% filter(Departure.station.name %in% stations_no_coords$Departure.station.name) %>% View()
  # Some of these still have namesakes in "stations" with coordinates, hmm
  # These connections only happened now, because they do not share an ID nor a name with anything in stations_HSL
  # But one of their namesakes has an entry in stations_HSL by ID (and not name!)
# Let's connect those few up:
tmp <- left_join(stations_no_coords, stations[!is.na(x), c("Departure.station.name","x","y")], 
                       by="Departure.station.name", suffix=c("","_byNamesake"))
stations[Departure.station.name %in% stations_no_coords$Departure.station.name & is.na(x),
         ':=' (x = tmp[Departure.station.name==tmp$Departure.station.name]$x_byNamesake,
               y = tmp[Departure.station.name==tmp$Departure.station.name]$y_byNamesake)]
rm(tmp)
stations_no_coords <- stations %>% filter(is.na(x))
  # Ok, just 13 mystery location stations remaining now
stations_no_coords %>%
  summarise(Rides_total = sum(Rides_total)/sum(stations$Rides_total)*100)
  # Only 0.2% of rides have departed from those
# I will keep those stations in as they are real, public stations - but they will be useless in the application


#*------ Removing name variable --------------------
# Name was useful because we could fill out a good number of coordinates based name matches
# Now, however, we only want to keep one line for each station ID, and names get in the way of that
nrow(stations) # 723
stations %>% select(Departure.station.id) %>% unique() %>% nrow() # 622

# Checking that an ID's instances all share the same coordinates:
stations %>% select(Departure.station.id, x, y) %>% unique() %>% nrow() 
  # 622, same number as unique IDs, good

tmp <- stations %>% group_by(Departure.station.id) %>% 
  summarise(Rides_total = sum(Rides_total))
stations <- stations %>% select(-Departure.station.name, -Rides_total) %>% left_join(tmp) %>% unique()


#*------ Saving the station data from rides --------------------
write.csv(stations, paste0(folder, "/results/stations_fromRides.csv"))
saveRDS(stations, paste0(folder_bigdata, "/stations_fromRides.RDs"))
#stations <- readRDS(paste0(folder_bigdata, "/stations_fromRides.RDs"))



#* TABLE OF STATIONS IN TIME ------------------------------------------------------
period_start <- as.POSIXct("2016-05-01 00:00:00") # time before the first ride
period_end <- as.POSIXct("2023-11-01 23:59:59") # time after the last ride
# (Is_zerolength definition is based on the EDA done in the code eda.R)
rides_period <- rides[Departure >= period_start & Departure <= period_end] %>%
  mutate(Is_zerolength = ifelse(Departure.station.id==Return.station.id & 
                                  ((!is.na(Duration) & (Duration<60)) | 
                                     (!is.na(Covered.distance) & Covered.distance<50)), 1, 0))

# Use these "breaks" and "Departure.timeperiod" for a different breakdown than 1-minute intervals:
# breaks <- seq(round(period_start,"hour"), round(period_end,"hour"), by="15 min")
# rides_period$Departure.timeperiod <- cut(rides_period$Departure, breaks)

stations_intime <- rides_period %>%
  # for grouping by minutes, Departure (that is the greatest possible accuracy);
  # for any other length of time, set up and use Departure.timeperiod:
  group_by(Departure, Departure.station.id) %>% 
  summarise(Rides_total = n(),
            Rides_zerolength = sum(Is_zerolength)) %>%
  mutate(Rides_zerolength_prop = round(Rides_zerolength/Rides_total, 2)) %>%
  left_join(stations[, c("Departure.station.id", "x", "y")], by="Departure.station.id")
# Removing rides from stations we deemed not useful:
stations_intime <- stations_intime[Departure.station.id %in% stations$Departure.station.id,] 
rm(rides_period)

# How many minutes have stations without coordinates?
table(is.na(stations_intime$x), useNA="i")
  # 39878 minutes ~ 27.7 hours
summary(stations_intime$Rides_zerolength_prop)

#*--- Saving the ride data in terms of stations in time --------------------
saveRDS(stations_intime, paste0(folder_bigdata, "/stations__2016_2023__1min.RDs"))
write.csv(stations_intime, paste0(folder_bigdata, "/stations__2016_2023__1min.csv"))
#stations_intime <- read.csv(paste0(folder_bigdata, "/stations__2016_2023__1min.csv"))

# For writing the years in individual csv-s:
for (i in c(2016:2023)) {
  stations_intime_i <- stations_intime[year(stations_intime$Departure)==i,]
  write.csv(stations_intime_i, paste0(folder_bigdata, 
                                      "/stations__2016_2023__1min/stations_", i, "_1min.csv"))
}


