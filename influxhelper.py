import os
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

def last_row_to_influx(df):
    # Credentials
    INFLUXDB_TOKEN = os.environ.get("INFLUXDB_TOKEN")
    INFLUXDB_BUCKET = os.environ.get("INFLUXDB_BUCKET")
    ORG = os.environ.get("ORG")
    URL = os.environ.get("URL")

    measurement_name = "zisterne_oas"

    try:
        client = InfluxDBClient(url=URL, token=INFLUXDB_TOKEN, org=ORG)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        
        row_df = df.iloc[-1]

        point = Point(measurement_name)
        
        for col in df.columns:
            point.field(col, row_df[col])
        
        point.time(row_df.name, WritePrecision.NS)
        
        # Write the point to InfluxDB
        write_api.write(bucket=INFLUXDB_BUCKET, org=ORG, record=point)
        print("Data successfully written to InfluxDB.")
    except Exception as e:
        print(f"Error writing data to InfluxDB: {e}")
