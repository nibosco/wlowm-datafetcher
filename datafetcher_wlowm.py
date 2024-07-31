# -*- coding: utf-8 -*-
import pandas as pd
import json
from datetime import datetime
import requests
import os
from openmeteo_apicall import get_weatherdata
from influxhelper import last_row_to_influx

#variables
csv_path = "/data/wlowm_data.csv"
liquidcheck_url = os.environ.get("URL_ENDPOINT", "http://liquid-check/infos.json")

#water level helpers
#API-Call to sensor
def fetch_data_from_api(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        json_data = response.json()
        return json_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from URL: {e}")
        return None
  
#filter_json
def filter_json(json_data):
    try:
        measure_data = json_data['payload']['measure']
        raw_data = measure_data['raw']
        age_data = measure_data['age']
        return {**raw_data, 'age': age_data}
    except KeyError:
        print("Error: Could not find required data in the JSON.")
        return None

#Script wlowm_data import
print("------\nFetching data started")
try:
    wlowm_df = pd.read_csv(csv_path, index_col="timestamp")
except:
    print("no CSV found, creating new one")
print("\nFetching data: waterlevel STARTED")
data = fetch_data_from_api(liquidcheck_url)
del(liquidcheck_url)
    
data = filter_json(data)
#level in m
#content in l
#age is "measurement was X seconds ago"

if data is not None:
    wl_df_tmp = pd.DataFrame([data])
    wl_df_tmp["timestamp"]=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    wl_df_tmp.set_index('timestamp', inplace=True)
    wl_df_tmp = wl_df_tmp.add_prefix("wl_")
    del(data)

else:
    print("No waterlevel json data")
print("Fetching data: waterlevel FINISHED")

#openmeteo data fetch
print("\nFetching data: openmeteo STARTED")
owm_df_daily, owm_df_hourly, owm_df_current = get_weatherdata()
#adding prefixes related to the source d = daily h = hourly c = current
print("\nFetching data: openmeteo FINISHED")

#daily data
data={}
for index, row in owm_df_daily.iterrows():
    #sketchy fix for timedelta 
    delta_d = (row["date"].replace(microsecond=0, second=0, minute=0, hour=0) - datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)).days
    if delta_d > 0:
        delta_d = f'+{delta_d}'
    else:
        pass
    if -4 <= int(delta_d) <= 5: #limit past and prediction values
        for column in ['temperature_2m_max', 'temperature_2m_min', 'sunshine_duration',
               'uv_index_max', 'precipitation_sum', 'rain_sum']:
            column_slug = f'd_{column}_{delta_d}'
            data[column_slug] = row[column]    

#hourly data
#pre-processing daily mean
owm_df_hourly["date"] = pd.to_datetime(owm_df_hourly["date"])
owm_df_hourly_d = owm_df_hourly.groupby(owm_df_hourly['date'].dt.date).mean()

for index, row in owm_df_hourly_d.iterrows():
    delta_d = (row["date"] - datetime.now()).days
    if delta_d > 0:
        delta_d = f'+{delta_d}'
    else:
        pass
    if -4 <= int(delta_d) <= 5:
        for column in ['soil_moisture_3_to_9cm', 'soil_moisture_9_to_27cm',
               'soil_moisture_27_to_81cm']:
            column_slug = f'h_{column}_{delta_d}'
            data[column_slug] = row[column]      
del(owm_df_hourly, owm_df_hourly_d)

#current data
owm_df_current = owm_df_current.add_prefix("c_")
data_tmp = owm_df_current.to_dict(orient='records')[0]
data.update(data_tmp)
del(data_tmp, column_slug, column, delta_d, row, index,)

owm_df_tmp = pd.DataFrame([data])
owm_df_tmp.set_index(wl_df_tmp.index, inplace=True)
#adding prefixes related to the source d = daily h = hourly c = current
owm_df_tmp= owm_df_tmp.add_prefix("owm_")
del(data)

wlowm_df_tmp = pd.concat([wl_df_tmp, owm_df_tmp], axis=1)
if 'wlowm_df' in locals():
    # if df exists, append the new row
    wlowm_df = pd.concat([wlowm_df, wlowm_df_tmp], ignore_index=False)
else:
    wlowm_df = wlowm_df_tmp
print(f'\nData sources merged successfully into:\nwlowm_df ({wlowm_df.shape})')

#sketchy timedelta handling (e.g. service running at 00:00:00 generates NaN values due to timedelta; using ffill method for affected cols)
cols = wlowm_df.filter(regex=r'^owm_d.*\+5$', axis=1).columns
if not wlowm_df.empty:
    if wlowm_df.loc[wlowm_df.tail(1).index, cols].isna().any(axis=1).any():
        print(f'\nNaN values for columns: \n{cols} detected!')
        wlowm_df.loc[wlowm_df.tail(2).index, cols] = wlowm_df.tail(2)[cols].ffill()
        if not wlowm_df.loc[wlowm_df.tail(1).index, cols].isna().any(axis=1).any():
            print(f'\nNaN values were successfully filled using the ffill() method')
    else:
        pass
else:
    pass
del(cols)

#Saving to csv
wlowm_df.to_csv(csv_path)

#Saving to influx
if os.environ.get("INFLUXDB_TOKEN"):
    last_row_to_influx(wlowm_df)
    
print("------\nFetching data FINISHED\n------")


