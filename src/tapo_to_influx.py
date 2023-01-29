import datetime
import os
import sys

from influxdb import InfluxDBClient
from PyP100 import PyP110

which_day = [int(i) for i in sys.argv[1].split("-")]
start_timestamp = int(datetime.datetime(*which_day).timestamp())
end_timestamp = start_timestamp + 24 * 3600

client = InfluxDBClient(host=os.environ["DOCKER_IP"], port=8086)
client.create_database("power_usage")
client.switch_database("power_usage")

ips = os.environ["TAPO_IPS"].split()

data = []
for ip in ips:
    plug = PyP110.P110(ip, os.environ["TPLINK_LOGIN"], os.environ["TPLINK_PASSWORD"])
    plug.handshake()
    plug.login()
    name = plug.getDeviceName()

    for hour, value in enumerate(
        plug.getEnergyData(start_timestamp, end_timestamp, 60)["result"]["data"]
    ):
        timestamp = int(datetime.datetime(*which_day, hour, 59).timestamp())
        data.append(f"usage,name={name} value={value} {timestamp}")

client.write_points(data, database="power_usage", protocol="line", time_precision="s")
