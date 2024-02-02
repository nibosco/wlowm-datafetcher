import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import os
from datetime import datetime

def get_weatherdata():    
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)
    
    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
    	"latitude": os.environ["LATITUDE"],
    	"longitude": os.environ["LONGITUDE"],
    	"current": ["temperature_2m", "relative_humidity_2m", "precipitation", "rain", "surface_pressure"],
    	"hourly": ["soil_moisture_3_to_9cm", "soil_moisture_9_to_27cm", "soil_moisture_27_to_81cm"],
    	"daily": ["temperature_2m_max", "temperature_2m_min", "sunshine_duration", "uv_index_max", "precipitation_sum", "rain_sum"],
    	"timezone": os.environ.get("TIMEZONE", "Europe/Berlin"),
    	"past_days": 3
    }
    responses = openmeteo.weather_api(url, params=params)
    
    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"\nCoordinates {response.Latitude()}°E {response.Longitude()}°N")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")
    print(f"Accessed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Current values. The order of variables needs to be the same as requested.
    current = response.Current()
    current_temperature_2m = current.Variables(0).Value()
    current_relative_humidity_2m = current.Variables(1).Value()
    current_precipitation = current.Variables(2).Value()
    current_rain = current.Variables(3).Value()
    current_surface_pressure = current.Variables(4).Value()
    
    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_soil_moisture_3_to_9cm = hourly.Variables(0).ValuesAsNumpy()
    hourly_soil_moisture_9_to_27cm = hourly.Variables(1).ValuesAsNumpy()
    hourly_soil_moisture_27_to_81cm = hourly.Variables(2).ValuesAsNumpy()
    
    hourly_data = {"date": pd.date_range(
    	start = pd.to_datetime(hourly.Time(), unit = "s"),
    	end = pd.to_datetime(hourly.TimeEnd(), unit = "s"),
    	freq = pd.Timedelta(seconds = hourly.Interval()),
    	inclusive = "left"
    )}
    hourly_data["soil_moisture_3_to_9cm"] = hourly_soil_moisture_3_to_9cm
    hourly_data["soil_moisture_9_to_27cm"] = hourly_soil_moisture_9_to_27cm
    hourly_data["soil_moisture_27_to_81cm"] = hourly_soil_moisture_27_to_81cm
    
    hourly_dataframe = pd.DataFrame(data = hourly_data)
    #print(hourly_dataframe)
    
    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
    daily_sunshine_duration = daily.Variables(2).ValuesAsNumpy()
    daily_uv_index_max = daily.Variables(3).ValuesAsNumpy()
    daily_precipitation_sum = daily.Variables(4).ValuesAsNumpy()
    daily_rain_sum = daily.Variables(5).ValuesAsNumpy()
    
    daily_data = {"date": pd.date_range(
    	start = pd.to_datetime(daily.Time(), unit = "s"),
    	end = pd.to_datetime(daily.TimeEnd(), unit = "s"),
    	freq = pd.Timedelta(seconds = daily.Interval()),
    	inclusive = "left"
    )}
    daily_data["temperature_2m_max"] = daily_temperature_2m_max
    daily_data["temperature_2m_min"] = daily_temperature_2m_min
    daily_data["sunshine_duration"] = daily_sunshine_duration
    daily_data["uv_index_max"] = daily_uv_index_max
    daily_data["precipitation_sum"] = daily_precipitation_sum
    daily_data["rain_sum"] = daily_rain_sum
    
    daily_dataframe = pd.DataFrame(data = daily_data)
    #print(daily_dataframe)
    
    #create current_dataframe
    current_dataframe = pd.DataFrame({
    "current_temperature": current_temperature_2m,
    "current_relative_humidity_2m": current_relative_humidity_2m,
    "current_precipitation": current_precipitation,
    "current_rain": current_rain,
    "current_surface_pressure": current_surface_pressure},
    index=[0])

    
    return (daily_dataframe, hourly_dataframe, current_dataframe)


