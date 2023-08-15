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

# run this from the root env of the monorepo (the BusMonitor folder)
load_dotenv()
load_dotenv(f"{parent_directory}/.env")

SPTRANS_KEY = os.getenv("SPTRANS_KEY")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")

if not SPTRANS_KEY:
	raise Exception("SPTRANS_KEY not set")
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

SPTRANS_BASE_URL = "http://api.olhovivo.sptrans.com.br/v2.1"

engine = sqlalchemy.create_engine(
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
)

def get_position(line_id):
	s = requests.session()
	auth = s.post(f'{SPTRANS_BASE_URL}/Login/Autenticar?token={SPTRANS_KEY}', timeout=30)
	assert auth.text == 'true'
	# print(auth)
	# print(auth.request.headers)
	resp = s.get(f"{SPTRANS_BASE_URL}/Posicao/Linha?codigoLinha={line_id}", verify=False)
	resp.raise_for_status()

	dict_ = resp.json()
	if not dict_.get('vs'):
		raise Exception(f"no data found for line {line_id}")

	hour, minute = dict_['hr'].split(':')
	latitude = dict_['vs'][0]['py']
	longitude = dict_['vs'][0]['px']

	return {
		"timestamp": datetime.datetime.combine(
			datetime.datetime.now(pytz.timezone('America/Sao_Paulo')).date(), 
			datetime.time(int(hour), int(minute), 0)),
		"latitude": latitude,
		"longitude": longitude,
	}

bus_names = {
	2023: "8012-10-2023",
	34791: "8012-10-34791",
	2085: "8022-10-2085",
	2545: "8032-10-2545",
	34098: "702U-10-34098",
	657: "701U-10-657",
}
while True:
	print('----- START')
	positions = []
	for position_id in list(bus_names.keys()):
		print(" -- > ")
		print(f"getting position for {position_id} ({datetime.datetime.now()})")
		try:
			position = get_position(position_id)
			print(position)
				
			position['bus_id'] = bus_names[position_id]
			positions.append(position)

			# df = pd.read_sql_table(POSTGRES_TABLE, engine, schema=POSTGRES_SCHEMA)

		except Exception as e:
			print(f"error fetching position {position_id}:", e)
			continue
		time.sleep(5)
		print(" < -- ")
	
	try:
		df = pd.DataFrame(positions)

		df.to_sql(
			POSTGRES_TABLE, 
			engine, 
			if_exists='append', 
			index=False, 
			schema=POSTGRES_SCHEMA, 
			method=postgres_upsert("pk_locations")
		)
	except Exception as e:
		print("error in .to_sql():", e)
		continue
		
	print('----- END (sleeping...)')
	time.sleep(5)
