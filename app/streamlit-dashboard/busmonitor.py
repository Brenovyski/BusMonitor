import streamlit as st
import psycopg2
import pandas as pd
import folium
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

# Load bus data into DataFrame
bus_query = "SELECT longitude, latitude, measurement_time, bus_name FROM buses_table;"
bus_rows = run_query(bus_query)
bus_data = pd.DataFrame(bus_rows, columns=['longitude', 'latitude', 'measurement_time', 'bus_name'])
bus_data['measurement_time'] = pd.to_datetime(bus_data['measurement_time'])
bus_data['measurement_date'] = bus_data['measurement_time'].dt.date

# Load bus stops data into DataFrame
stop_query = "SELECT stop_name, latitude, longitude FROM bus_stops;"
stop_rows = run_query(stop_query)
stop_data = pd.DataFrame(stop_rows, columns=['stop_name', 'latitude', 'longitude'])

# Date filter
min_date = bus_data['measurement_date'].min()
max_date = bus_data['measurement_date'].max()
date_filter = st.date_input('Select date range', min_value=min_date, max_value=max_date, value=(min_date, max_date))

# Filter bus data using the selected date range
filtered_bus_data = bus_data[(bus_data['measurement_date'] >= date_filter[0]) & (bus_data['measurement_date'] <= date_filter[1])]

# Bus selection
bus_options = st.multiselect('Select buses', options=bus_data['bus_name'].unique(), default=bus_data['bus_name'].unique())
filtered_data = filtered_bus_data[filtered_bus_data['bus_name'].isin(bus_options)]

# Create a map with Stamen Toner tiles
m = folium.Map(location=[stop_data['latitude'].mean(), stop_data['longitude'].mean()], zoom_start=15)

# Add bus stops to the map (blue markers)
for index, row in stop_data.iterrows():
    folium.Marker([row['latitude'], row['longitude']], popup=row['stop_name'], icon=folium.Icon(color='blue', icon='bus', prefix="fa")).add_to(m)

# Add buses to the map (custom icon)
for index, row in filtered_data.iterrows():
    folium.Marker([row['latitude'], row['longitude']], popup=row['bus_name'], icon=folium.Icon(color='red', icon="location-pin", prefix="fa")).add_to(m)

# Display the map in Streamlit
folium_static(m)

# Show raw data
if st.checkbox('Show raw data'):
    st.subheader('Bus Data')
    st.write(filtered_data)
    st.subheader('Bus Stop Data')
    st.write(stop_data)