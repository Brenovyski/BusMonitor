# BusMonitor

Need to create your own Database in postgres for development
(put the secrets in .streamlit/secrets.toml)

[postgres]
host = "database-1.c3pulzlhrdfe.us-east-1.rds.amazonaws.com"
port = 5432
dbname = "labredes"
user = "<>"
password = "<>"


Development example
![Captura de tela 2023-08-11 002829](https://github.com/Brenovyski/BusMonitor/assets/85632063/c35dba21-9c5a-487a-9bf6-dac1d917555d)

# Checklist

- [X] Monitor the real-time position of buses using GPS data.
- [] Calculate and display the average speed of the bus between specific points.
- [] Check if the vehicle has been stopped for more than 5 minutes and generate an alert to the monitoring center.
- [] Check if the bus is running late compared to the scheduled time and generate an alert if the delay is considered long.
- [] Check if the bus is within the speed limits of the roads it travels on and generate an alert if the speed is exceeded.
- [] Display the current position of the bus to passengers.
- [] Generate an alert for passengers when the bus is near a certain point.
- [] Calculate the estimated time for the bus to reach the next stop and display this information to passengers.
 
 
 
 
 
 
 
 