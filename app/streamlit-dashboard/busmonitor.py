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
@st.cache_data(ttl=10)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

bus_query = "WITH RankedLocations AS (SELECT timestamp AS measurement_time, bus_id AS bus_name, latitude, longitude, ROW_NUMBER() OVER (PARTITION BY bus_id ORDER BY timestamp DESC) AS rn FROM labredes.tracking.locations) SELECT measurement_time, bus_name, latitude, longitude FROM RankedLocations WHERE rn = 1;"
bus_rows = run_query(bus_query)
bus_data = pd.DataFrame(bus_rows, columns=['measurement_time', 'bus_name', 'latitude', 'longitude'])

# Define colors for specific bus lines
bus_colors = {
    "CAIO-0001": "red",
    "8012-10-2023": "purple",
    "8012-10-34791": "green",
    "8022-10-2085": "orange",
    "8032-10-2545": "darkred",
    "702U-10-34098": "darkblue",
    "701U-10-657": "pink",
}

# Bus selection
bus_options = st.multiselect('Select buses', options=bus_colors.keys(), default=list(bus_colors.keys()))

# Read the CSV file (for bus stops)
try:
    bus_stops_df = pd.read_csv('stops.csv', header=None)
except:
    bus_stops_df = pd.read_csv('app/streamlit-dashboard/stops.csv', header=None)
bus_stops = [(row[3], row[4], row[1]) for index, row in bus_stops_df.iterrows()]

# Create a map 
m = folium.Map(location=[bus_stops[0][0], bus_stops[0][1]], zoom_start=14)

# Add bus stops to the map
for stop in bus_stops:
    lat, lon, name = stop
    folium.Marker([lat, lon], popup=name, icon=folium.Icon(color='blue', icon='bus', prefix='fa')).add_to(m)

# Add buses to the map
for index, row in bus_data.iterrows():
    if row['bus_name'] in bus_options:
        color = bus_colors.get(row['bus_name'], 'gray')  # Use 'gray' for buses not in the defined list
        folium.Marker([row['latitude'], row['longitude']], popup=row['bus_name'], icon=folium.Icon(color=color, icon="location-pin", prefix="fa")).add_to(m)
        folium.map.Marker(
            [row['latitude'], row['longitude']],
            icon=folium.DivIcon(html=f"<div style='color: {color};'>{row['bus_name']}</div>")
        ).add_to(m)

# Display the map in Streamlit
folium_static(m)

# Display bus names and their respective colors in a table
if st.checkbox('Show bus color'):
    st.subheader('Bus Color')
    colors_table = pd.DataFrame.from_dict(bus_colors, orient='index', columns=['Color']).reset_index()
    colors_table.columns = ['Bus Name', 'Color']
    st.write(colors_table)

# Show raw data
if st.checkbox('Show raw data'):
    st.subheader('Bus Data')
    st.write(bus_data)
    st.subheader('Bus Stop Data')
    st.write(pd.DataFrame(bus_stops, columns=['latitude', 'longitude', 'stop_name']))

st_autorefresh(interval=30000, limit=10_000_000, key="autorefresh")