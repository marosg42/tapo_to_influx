import datetime
import os
import requests
import sys

from enum import IntEnum
from influxdb import InfluxDBClient
from PyP100 import PyP110, MeasureInterval


which_day = [int(i) for i in sys.argv[1].split("-")]
start_timestamp = int(datetime.datetime(*which_day).timestamp())
end_timestamp = start_timestamp + 24 * 3600

client = InfluxDBClient(host=os.environ["DOCKER_IP"], port=8086)
client.create_database("power_usage")
client.switch_database("power_usage")

ips = os.environ["TAPO_IPS"].split()

data = []
for ip in ips:
    print(f"Processing {ip}")
    plug = PyP110.P110(ip, os.environ["TPLINK_LOGIN"], os.environ["TPLINK_PASSWORD"])
    try:
        plug.handshake()
    except requests.exceptions.ConnectTimeout as e:
        print(e)
        continue
    except Exception as e:
        if "Failed to initialize protocol" in str(e):
            print(f"Failed to initialize protocol for {ip}")
            continue
        else:
            raise (e)
    plug.login()
    name = plug.getDeviceName()
    print(f"Device name with {ip} is {name}")
    for hour, value in enumerate(
        plug.getEnergyData(start_timestamp, end_timestamp, MeasureInterval.HOURS)[
            "data"
        ]
    ):
        timestamp = int(datetime.datetime(*which_day, hour, 59).timestamp())
        data.append(f"usage,name={name} value={value} {timestamp}")

client.write_points(data, database="power_usage", protocol="line", time_precision="s")
