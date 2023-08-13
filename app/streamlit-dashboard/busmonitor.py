import streamlit as st
import psycopg2
import pandas as pd
import folium
from streamlit_autorefresh import st_autorefresh
from streamlit_folium import folium_static

st.title('BusMonitor: An Elegant Bus Monitoring System')

# Initialize connection
@st.cache_resource
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])

conn = init_connection()

# Perform query
@st.cache_data(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

bus_query = "WITH RankedLocations AS (SELECT timestamp AS measurement_time, bus_id AS bus_name, latitude, longitude, ROW_NUMBER() OVER (PARTITION BY bus_id ORDER BY timestamp DESC) AS rn FROM labredes.tracking.locations) SELECT measurement_time, bus_name, latitude, longitude FROM RankedLocations WHERE rn = 1;"
bus_rows = run_query(bus_query)
bus_data = pd.DataFrame(bus_rows, columns=['measurement_time', 'bus_name', 'latitude', 'longitude'])
bus_data['measurement_time'] = pd.to_datetime(bus_data['measurement_time'])
bus_data['measurement_date'] = bus_data['measurement_time'].dt.date

# Filter out any None or NaN values from the measurement_date column
valid_dates = bus_data['measurement_date'].dropna()

# If there are valid dates, use them to set the min and max values for the date input
if not valid_dates.empty:
    min_date = valid_dates.min()
    max_date = valid_dates.max()
    selected_date = st.date_input('Select date', min_value=min_date, max_value=max_date, value=min_date)
else:
    st.error("No valid dates found in the data.")
    selected_date = None

# Filter bus data using the selected date
filtered_bus_data = bus_data[bus_data['measurement_date'] == selected_date]

# Bus selection
bus_options = st.multiselect('Select buses', options=filtered_bus_data['bus_name'].unique(), default=filtered_bus_data['bus_name'].unique())

# Read the CSV file (for bus stops)
bus_stops_df = pd.read_csv('stops.csv', header=None)
bus_stops = [(row[3], row[4], row[1]) for index, row in bus_stops_df.iterrows()]

# Create a map 
m = folium.Map(location=[bus_stops[0][0], bus_stops[0][1]], zoom_start=14)

# Add bus stops to the map
for stop in bus_stops:
    lat, lon, name = stop
    folium.Marker([lat, lon], popup=name, icon=folium.Icon(color='blue', icon='bus', prefix='fa')).add_to(m)

# Add buses to the map
for index, row in filtered_bus_data.iterrows():
    if row['bus_name'] in bus_options:
        folium.Marker([row['latitude'], row['longitude']], popup=row['bus_name'], icon=folium.Icon(color='red', icon="location-pin", prefix="fa")).add_to(m)

# Display the map in Streamlit
folium_static(m)

# Show raw data
if st.checkbox('Show raw data'):
    st.subheader('Bus Data')
    st.write(filtered_bus_data)
    st.subheader('Bus Stop Data')
    st.write(pd.DataFrame(bus_stops, columns=['latitude', 'longitude', 'stop_name']))

st_autorefresh(interval=30000, limit=10_000_000, key="autorefresh")