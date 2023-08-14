import streamlit as st
import psycopg2
import pandas as pd
from math import sin, cos, sqrt, atan2, radians
import folium
from streamlit_autorefresh import st_autorefresh
from streamlit_folium import folium_static

st.set_page_config(
    page_title="BusMonitor",
    page_icon="🚌",
    initial_sidebar_state="collapsed",
)

st.title('BusMonitor: An Elegant Bus Monitoring System')

# Haversine formula to calculate the distance between two lat/long points
def haversine(lon1, lat1, lon2, lat2):
    R = 6371.0  # Radius of the Earth in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def calculate_distance(group):
    distance = 0
    for i in range(1, len(group)):
        lon1, lat1, lon2, lat2 = group.iloc[i-1]['longitude'], group.iloc[i-1]['latitude'], group.iloc[i]['longitude'], group.iloc[i]['latitude']
        distance += haversine(lon1, lat1, lon2, lat2)
    return distance

def calculate_average_speed(group):
    distance = 0
    for i in range(1, len(group)):
        lon1, lat1, lon2, lat2 = group.iloc[i-1]['longitude'], group.iloc[i-1]['latitude'], group.iloc[i]['longitude'], group.iloc[i]['latitude']
        distance += haversine(lon1, lat1, lon2, lat2)

    time_difference = (group.iloc[-1]['measurement_time'] - group.iloc[0]['measurement_time']).total_seconds() / 3600 # Difference in hours
    if time_difference == 0:
        return 0 # To avoid division by zero
    return distance / time_difference

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

# Read the CSV file (for bus stops)
try:
    bus_stops_df = pd.read_csv('stops.csv', header=None)
except:
    bus_stops_df = pd.read_csv('app/streamlit-dashboard/stops.csv', header=None)
bus_stops = [(row[3], row[4], row[1]) for index, row in bus_stops_df.iterrows()]

# Bus selection
bus_options = st.multiselect('Select buses', options=bus_data['bus_name'].unique(), default=bus_data['bus_name'].unique())
bus_data = bus_data[bus_data['bus_name'].isin(bus_options)]

with st.expander('Most Recent Positions Map'):
    
    if st.checkbox('Most Recent Positions'):
        # st.write(bus_data)
        st.dataframe(bus_data, use_container_width=True, hide_index=True)

    if st.checkbox('Bus Stops'):
        # st.write(pd.DataFrame(bus_stops, columns=['latitude', 'longitude', 'stop_name']))
        st.dataframe(pd.DataFrame(bus_stops, columns=['latitude', 'longitude', 'stop_name']), use_container_width=True, hide_index=True)

    if st.checkbox("Show positions map"):
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
        folium_static(m, width=670)

with st.expander('Historical Positions (per bus) Map'):
    hist_bus_option = st.selectbox('Select buses', options=bus_data['bus_name'].unique(), index=0)
    hist_bus_query = f"WITH RankedLocations AS (SELECT timestamp AS measurement_time, bus_id AS bus_name, latitude, longitude, ROW_NUMBER() OVER (PARTITION BY bus_id ORDER BY timestamp DESC) AS rn FROM labredes.tracking.locations) SELECT measurement_time, bus_name, latitude, longitude FROM RankedLocations WHERE rn <= 5;"
    hist_bus_rows = run_query(hist_bus_query)
    hist_bus_data = pd.DataFrame(hist_bus_rows, columns=['measurement_time', 'bus_name', 'latitude', 'longitude'])
    hist_bus_data = hist_bus_data[hist_bus_data['bus_name'] == hist_bus_option]
    hist_bus_data['measurement_time'] = pd.to_datetime(hist_bus_data['measurement_time'])
    hist_bus_data = hist_bus_data.sort_values(['bus_name', 'measurement_time'])
    hist_bus_data = hist_bus_data[hist_bus_data['bus_name'].isin(bus_options)]

    if st.checkbox("Historical Positions"):
        st.dataframe(hist_bus_data, use_container_width=True, hide_index=True)

    if st.checkbox("Show historical positions map"):
        hist_map = folium.Map(location=[bus_stops[0][0], bus_stops[0][1]], zoom_start=14)

        # Add bus stops to the map
        for stop in bus_stops:
            lat, lon, name = stop
            folium.Marker([lat, lon], popup=name, icon=folium.Icon(color='blue', icon='bus', prefix='fa')).add_to(hist_map)
        
        # Add historical postions of a selected bus
        for index, row in hist_bus_data.iterrows():
            if row['bus_name'] == hist_bus_option:
                color = bus_colors.get(row['bus_name'], 'gray')  
                folium.Marker([row['latitude'], row['longitude']], popup=row['bus_name'], icon=folium.Icon(color=color, icon="location-pin", prefix="fa")).add_to(hist_map)
                folium.map.Marker(
                    [row['latitude'], row['longitude']],
                    icon=folium.DivIcon(html=f"<div style='color: {color};'>{row['bus_name']}</div>")
                ).add_to(hist_map)

        # Display the map in Streamlit
        folium_static(hist_map, width=670)  

    
# Show raw data
with st.expander('Bus Colors'):
    colors_table = pd.DataFrame.from_dict(bus_colors, orient='index', columns=['Color']).reset_index()
    colors_table.columns = ['Bus Name', 'Color']
    st.dataframe(colors_table, use_container_width=True, hide_index=True)

with st.expander('Past Positions, Average Speed and Distance Traveled'):
    st.write("Recent average speed and total distance traveled by each bus")
    number_of_records = st.number_input('Use last N records to compute speed and distance: ', min_value=1, max_value=100, value=10, step=1)
    bus_query = f"WITH RankedLocations AS (SELECT timestamp AS measurement_time, bus_id AS bus_name, latitude, longitude, ROW_NUMBER() OVER (PARTITION BY bus_id ORDER BY timestamp DESC) AS rn FROM labredes.tracking.locations) SELECT measurement_time, bus_name, latitude, longitude FROM RankedLocations WHERE rn <= {number_of_records};"
    bus_rows = run_query(bus_query)
    bus_data = pd.DataFrame(bus_rows, columns=['measurement_time', 'bus_name', 'latitude', 'longitude'])
    bus_data['measurement_time'] = pd.to_datetime(bus_data['measurement_time'])
    bus_data = bus_data.sort_values(['bus_name', 'measurement_time'])
    bus_data = bus_data[bus_data['bus_name'].isin(bus_options)]

    if st.checkbox('Show past positions'):
        st.dataframe(bus_data, use_container_width=True, hide_index=True)
    
    average_speeds = bus_data.groupby('bus_name').apply(calculate_average_speed).reset_index(name='average_speed')
    total_distances = bus_data.groupby('bus_name').apply(calculate_distance).reset_index(name='total_distance')

    # Merging the two dataframes
    merged_data = pd.merge(average_speeds, total_distances, on='bus_name')
    st.write("Distance Traveled (km) and Average Speeds (km/h):")
    st.dataframe(merged_data, use_container_width=True, hide_index=True)

st_autorefresh(interval=30000, limit=10_000_000, key="autorefresh")