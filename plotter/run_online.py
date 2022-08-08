
#####################################################################
#                Online data visualizer with Dash
#  Run the app and go to http://localhost:9000
#####################################################################

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import time

import environment
environment.add_internal_sources_to_path()
import message
from data_storage import DataStorage


#####################################################################
#                    Not config, don't change
#####################################################################

# path to storage directory, where all ProjectX data and backups are stored
STORAGE_DIRECTORY_PATH = "../binaries"

SERVER_PORT = 9000

REFRESH_INTERVAL = 30000


#####################################################################
#                       Data preparation
#####################################################################

def create_dateframe():
    data = pd.DataFrame({"timestamp": [],
                         "temperature": [],
                         "humidity": []})
    messages_list = _read_data_from_storage()
    data["timestamp"], data["temperature"], data["humidity"] = _reshape_data(messages_list)

    # not very smart timezone correction, but I had problems with tz_localize
    ONE_HOUR = 3600
    timezone_offset = ONE_HOUR          #Central European Time (UTC+1)
    if _is_summertime():
        timezone_offset += ONE_HOUR     #Central European Summer Time (UTC+2)
    data["timestamp"] = [timestamp + timezone_offset for timestamp in data["timestamp"]]

    data["timestamp"] = pd.to_datetime(data["timestamp"], unit='s')
    return data

def _read_data_from_storage():
    dir_path = environment.get_directory_path() / STORAGE_DIRECTORY_PATH
    storage = DataStorage(False, dir_path)
    data = storage.read_all_data()
    data = message.parse_messages(data)
    print(f"     Stored messages count: {len(data)}")
    if len(data) > 0:
        print(f"     Last message: {message.format(data[-1])}\n")
    return data

def _reshape_data(messages: list):
    timestamps, temperatures, humidities = [], [], []
    for msg in messages:
        t, temp, hum = msg
        timestamps.append(t)
        temperatures.append(temp)
        humidities.append(hum)
    return timestamps, temperatures, humidities

def _is_summertime():
    # not entirely correct implementation, but it should be enough for everyday's use - one week accuracy
    month = time.localtime()[1]
    if month >= 4 and month <= 10:
        return True
    else:
        return False


#####################################################################
#                           Web server
#####################################################################

def create_figure():
    data = create_dateframe()
    # TODO to be changed:
    # - legend description and position
    # - second Y axis
    # - plot size/ratio
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    return px.line(x=data["timestamp"], 
                   y=[data["temperature"], data["humidity"]])

app = Dash(__name__)

app.layout = html.Div(style={'color': '#333333', 'font-family': 'Calibri', 'textAlign': 'center'}, children=[
    html.H2('Project X'),
    html.Div('Inner sensor measurements'),
    dcc.Graph(
        id = "measurements",
        figure = create_figure()
    ),
    dcc.Interval(
        id = "interval",
        interval = REFRESH_INTERVAL,
        n_intervals = 0
    ),
])

@app.callback(Output("measurements", "figure"),
        [Input("interval", "n_intervals")])
def update_plot_callback(n_intervals):
    return create_figure()

if __name__ == '__main__':
    app.run_server(port = SERVER_PORT)