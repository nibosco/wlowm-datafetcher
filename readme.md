# Data fetcher for Liquidcheck waterlevel sensor and open-meteo weather data :potable_water::cloud::open_file_folder:

A data fetching tool combining the waterlevel readings from a Liquid Check waterlevel sensor (by [SI-Elektronik](https://liquid-check-info.si-elektronik.de/ "Liquid Check waterlevel sensor")) and weather data provided by [open-meteo](https://open-meteo.com/ "open-meteo").
<br>
## Background :book:
A waterlevel sensor is used to monitor the water level of rainwater collection tank. The determining factor of the demand is the use case (predominantly irrigation). The supply is determined by the amount of rainwater collected. Both are expected to show correlations to meteorological data.  To analyze (and hopefully predict) waterlevels, relevant data needs to be gathered. A collection of meteorological data was selected (see [here](#result)).

# Usage
## **Configuration :gear:**
### **.env :page_facing_up:**

All config parameters can be changed in the .env file.<br>
For the open.meteo API-call the latitude, longitude and timezone need to be set. The given timezone is also used to set the timezone of the container itself.
The url-endpoint of the sensor needs to be set accordingly. See manufacturers documentation for that.<br>
The schedule for running the script is set using a cron job. Define the planned interval using ```CRON_INTERVAL``` in the crontab-format.<br>
```CSV_PATH``` is used to bind a host directory for data storage.


```python
#openmeteo params
LATITUDE=XX.XXXX
LONGITUDE=XX.XXXX
TIMEZONE="XYZ/XYZ"

#Liquid Check params
URL_ENDPOINT="XYZ" #(default: "http://liquid-check/infos.json")

#docker params
#docker-compose uses TIMEZONE for TZ of container

#cron scheduling (e.g. hourly)
CRON_INTERVAL=0 * * * *
#bind host directory for data-output
CSV_PATH=/PATH/on/host/data
```

## **Spinning up a container :ship:** 

Create container using docker compose and run it in the background

```docker
docker compose up -d
```
The data fetcher now runs periodically and writes gathered data into a csv-file.
<br>
## **Result**
The csv-ouput stores the values as following:<br>
| Parameter| Range| Information|
| --- | --- |--- |
| **Water level** | ||
| `timestamp`| current|`%Y-%m-%d %H:%M:%S`|
| `wl_level` | current |Water level in `m`|
| `wl_content` | current|Content in `l`|
| `wl_percent` | current |Level of filling in `%`|
| `wl_age` |current |Time elapsed since last measurement in `s`|
||
|**open-meteo weather data**||See open-meteo [documentation](https://open-meteo.com/en/docs "open-meteo doc")|
| `owm_d_temperature_2m_max` | -4 to +5| Maximum daily air temperature at 2 meters above ground|
| `owm_d_temperature_2m_min` | -4 to +5|Minimum daily air temperature at 2 meters above ground|
| `owm_d_sunshine_duration` | -4 to +5| The number of seconds of sunshine per day is determined by calculating direct normalized irradiance exceeding 120 W/m², following the WMO definition. Sunshine duration will consistently be less than daylight duration due to dawn and dusk.|
| `owm_d_uv_index_max` | -4 to +5 | 	Daily maximum in UV Index starting from 0.|
| `owm_d_precipitation_sum` | -4 to +5|Sum of daily precipitation (including rain, showers and snowfall)|
| `owm_d_rain_sum` | -4 to +5|Sum of daily rain|
| `owm_h_soil_moisture_3_to_9cm` | -4 to +5|Average soil water content as volumetric mixing ratio at 3-9 cm depth in m<sup>3</sup>. Daily means are calculated.|
| `owm_h_soil_moisture_9_to_27cm` | -4 to +5|Average soil water content as volumetric mixing ratio at 9-27 cm depth in m<sup>3</sup>. Daily means are calculated.|
| `owm_h_soil_moisture_27_to_82cm` | -4 to +5|Average soil water content as volumetric mixing ratio at 27-81 cm depth in m<sup>3</sup>. Daily means are calculated.|
| `owm_c_current_temperature`|current |`°C`|
| `owm_c_current_relative_humidity_2m`| current|`%`|
| `owm_c_current_rain`|current |`mm`|
| `owm_c_current_surface_pressure`|current |`hPa`|

_Range: The calculated timedelta in days between current time and gathered meteo data. All parameters are stored for each day (-4 days back and up to +5 days of forecast)._
<br>

# Appendix
## **open-meteo data** :clipboard:

The following selection of parameters is used for the api-call to [open-meteo](https://open-meteo.com/ "open-meteo").<br>
See details in the [```openmeteo_apicall.py```](openmeteo_apicall.py)

```
params ={
	"latitude": os.environ["LATITUDE"],
	"longitude": os.environ["LONGITUDE"],
	"current": ["temperature_2m", "relative_humidity_2m", "precipitation", "rain","surface_pressure"],
	"hourly": ["soil_moisture_3_to_9cm", "soil_moisture_9_to_27cm", "soil_moisture_27_to_81cm"],
	"daily": ["temperature_2m_max", "temperature_2m_min", "sunshine_duration", "uv_index_max", "precipitation_sum", "rain_sum"],
	"timezone": os.environ.get("TIMEZONE", "Europe/Berlin"),
	"past_days": 3
}
```
The selection can be easily adapted. Changes to the [```datafechter_wlowm.py```](datafechter_wlowm.py) and the data processing are necessary.<br>

# Outlook :telescope:

- supporting storing data into InfluxDB instance <br>
![Progress](https://progress-bar.dev/33/?title=pending)

- training model for waterlevel prediction<br>
![Progress](https://progress-bar.dev/1/?title=data-mining)
