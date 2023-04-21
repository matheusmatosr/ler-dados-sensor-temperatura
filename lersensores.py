import os
import glob
import time

from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

region = "us-east-1"
token = "gxuxe-VAPOZ3kEyyvvtQJl1RWOAYuAbQCrRK-V0D3kFwLpR0Vdx6icSJUPiqyXiX7u98W632p99QvQzf3W1Ncw=="
org = "9518899c4737accb"
bucket = "Cloud Sensores"

client = InfluxDBClient(url="https://us-east-1-1.aws.cloud2.influxdata.com", token="gxuxe-VAPOZ3kEyyvvtQJl1RWOAYuAbQCrRK-V0D3kFwLpR0Vdx6icSJUPiqyXiX7u98W632p99QvQzf3W1Ncw==")
write_api = client.write_api(write_options=SYNCHRONOUS)

query_api = client.query_api()

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'

device_folder = glob.glob(base_dir + '28*')[0]
device_folder1 = glob.glob(base_dir + '28*')[1]

device_file = device_folder + '/w1_slave'
device_file1 = device_folder1 + '/w1_slave'


def read_rom():
    name_file = device_folder+'/name'
    f = open(name_file,'r')
    return f.readline()

def read_rom1():
    name_file1 = device_folder1+'/name'
    g = open(name_file1,'r')
    return g.readline()


 
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp_raw1():
    g = open(device_file1, 'r')
    lines1 = g.readlines()
    g.close()
    return lines1



def read_temp():
    lines = read_temp_raw()
    while lines[1].strip()[-3:] != 'YES':
        lines = read_temp_raw()
        equals_pos = lines[1].find('t=')
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0

        data = [
            {
                "measurement": "temperature",
                "tags": {
                    "sensor": "sensor1"
                },
                "fields": {
                    "celsius": temp_c,
                    "fahrenheit": temp_f
                }
            }
        ]

        write_api.write(bucket="Cloud Sensores", org="9518899c4737accb", record=data)

    return temp_c, temp_f

def read_temp1():
    lines1 = read_temp_raw1()
    while lines1[1].strip()[-3:] != 'YES':
        lines1 = read_temp_raw1()
        equals_pos1 = lines1[1].find('t=')
        temp_string1 = lines1[1][equals_pos1+2:]
        temp_c1 = float(temp_string1) / 1000.0
        temp_f1 = temp_c1 * 9.0 / 5.0 + 32.0

        data = [
            {
                "measurement": "temperature",
                "tags": {
                    "sensor": "sensor2"
                },
                "fields": {
                    "celsius": temp_c1,
                    "fahrenheit": temp_f1
                }
            }
        ]

        write_api.write(bucket="Cloud Sensores", org="9518899c4737accb", record=data)

    return temp_c1, temp_f1

while True:
    print(' C1=%3.3f  F1=%3.3f'% read_temp())
    print(' C2=%3.3f  F2=%3.3f'% read_temp1())
    time.sleep(1)
