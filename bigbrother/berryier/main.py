# extract __file__ and append the ../../__file__ folder to sys.path
import os
import sys

# Get the absolute path of the current file's directory
current_directory = os.path.dirname(os.path.abspath(__file__))
# Go up two directories from the current directory
parent_directory = os.path.join(current_directory, '..', '..')
# Normalize the path (removing any redundant '..' or '.' components)
parent_directory = os.path.normpath(parent_directory)
sys.path.insert(0, parent_directory)

from dotenv import load_dotenv
import pandas as pd
import sqlalchemy
from utils.postgres import postgres_upsert
import requests
import time
import datetime
import pytz
import serial
import pynmea2

# run this from the root env of the monorepo (the BusMonitor folder)
load_dotenv()
load_dotenv(f"{parent_directory}/.env")

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")

if not POSTGRES_USER:
	raise Exception("POSTGRES_USER not set")
if not POSTGRES_PASSWORD:
	raise Exception("POSTGRES_PASSWORD not set")
if not POSTGRES_HOST:
	raise Exception("POSTGRES_HOST not set")

POSTGRES_PORT = 5432
POSTGRES_DATABASE = "labredes"
POSTGRES_SCHEMA = "tracking"
POSTGRES_TABLE = "locations"

engine = sqlalchemy.create_engine(
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
)

port="/dev/ttyS0"

while True:
	ser=serial.Serial(port, baudrate=9600, timeout=0.5)
	dataout = pynmea2.NMEAStreamReader()
	newdata=ser.readline()
	try:
		newdata = newdata.decode('utf-8')
	except Exception as e:
		print(f"error trying to decode data {e}")

	if newdata[0:6] == "$GPRMC":
		newmsg=pynmea2.parse(newdata)
		lat=newmsg.latitude
		lng=newmsg.longitude
		datetime_ = datetime.datetime.now(pytz.timezone('America/Sao_Paulo')).replace(tzinfo=None)
	
		print(f"[{datetime_}] Latitude= {lat} and Longitude= {lng}")

		df = pd.DataFrame(
			[
				{
					"timestamp": datetime_,
					"latitude": lat,
					"longitude": lng,
					"bus_id": "CAIO-0001",
				}
			]
		)

		df.to_sql(
			POSTGRES_TABLE, 
			engine, 
			if_exists='append', 
			index=False, 
			schema=POSTGRES_SCHEMA, 
			method=postgres_upsert("pk_locations")
		)

		sleepsec = 10
		print(f"Sleeping for {sleepsec} seconds...")
		time.sleep(sleepsec)