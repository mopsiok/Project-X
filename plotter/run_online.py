
#####################################################################
#                Online data visualizer with Dash
#  Run the app and go to http://localhost:9000
#####################################################################

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import time

import environment
environment.add_internal_sources_to_path()
import message
from data_storage import DataStorage
import DataProcessing


#####################################################################
#                    Not config, don't change
#####################################################################

# path to storage directory, where all ProjectX data and backups are stored
STORAGE_DIRECTORY_PATH = "../binaries"

SERVER_IP = '0.0.0.0' # needed for external connections
SERVER_PORT = 9000

REFRESH_INTERVAL = 5*60*1000            # plot refresh rate [in seconds]
SHOW_FILTERED_DATA = False              # filtering can be lagging for larger sets

TEMPERATURE_PRIMARY_COLOR = '#EF553B'
TEMPERATURE_SECONDARY_COLOR = '#AA2015'
TEMPERATURE_UNIT = u"\u00b0C"

HUMIDITY_PRIMARY_COLOR = '#636EFA'
HUMIDITY_SECONDARY_COLOR = '#3030AA'
HUMIDITY_UNIT = u"% RH"

PLOT_HEIGHT = 750
PLOT_PRIMARY_LINE_WIDTH = 2
PLOT_SECONDARY_LINE_WIDTH = 1

RESAMPLING_STEP = 30                    # requested time step in resampled data [in seconds]
LOW_PASS_CUTOFF_PERIOD = 1*60*60        # low pass filter cutoff period [in seconds]
LOW_PASS_ORDER = 3                      # low pass filter order

SECONDS_IN_HOUR = 3600.0

#####################################################################
#                       Data preparation
#####################################################################

def create_dateframe():
    data = pd.DataFrame({"timestamp": [],
                         "temperature": [],
                         "humidity": []})
    messages_list = _read_data_from_storage()
    
    time_raw, temp_raw, hum_raw = _reshape_data(messages_list)

    if SHOW_FILTERED_DATA:
        time_sampled, temp_sampled = DataProcessing.linearResampling(time_raw, temp_raw, RESAMPLING_STEP)
        _, hum_sampled = DataProcessing.linearResampling(time_raw, hum_raw, RESAMPLING_STEP)
        data["timestamp"], data["temperature"], data["humidity"] = time_sampled, temp_sampled, hum_sampled
        data["temperature_filtered"] = DataProcessing.lowPassFilter(temp_sampled, RESAMPLING_STEP, 1.0/LOW_PASS_CUTOFF_PERIOD, LOW_PASS_ORDER)
        data["humidity_filtered"] = DataProcessing.lowPassFilter(hum_sampled, RESAMPLING_STEP, 1.0/LOW_PASS_CUTOFF_PERIOD, LOW_PASS_ORDER)
    else:
        data["timestamp"], data["temperature"], data["humidity"] = time_raw, temp_raw, hum_raw

    # not very smart timezone correction, but I had problems with tz_localize
    timezone_offset = SECONDS_IN_HOUR          #Central European Time (UTC+1)
    if _is_summertime():
        timezone_offset += SECONDS_IN_HOUR     #Central European Summer Time (UTC+2)
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

    if SHOW_FILTERED_DATA:
        raw_temperature_color = TEMPERATURE_SECONDARY_COLOR
        raw_humidity_color = HUMIDITY_SECONDARY_COLOR
        raw_line_width = PLOT_SECONDARY_LINE_WIDTH
    else:
        raw_temperature_color = TEMPERATURE_PRIMARY_COLOR
        raw_humidity_color = HUMIDITY_PRIMARY_COLOR
        raw_line_width = PLOT_PRIMARY_LINE_WIDTH

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            name = "Temperature",
            x=data["timestamp"], y=data["temperature"],
            hovertemplate = "<b>%{y:.1f}" + TEMPERATURE_UNIT + "</b>",
            line = dict(color = raw_temperature_color, width = raw_line_width)
            ), 
        secondary_y = False,
        row=1, col=1
        )

    fig.add_trace(
        go.Scatter(
            name = "Humidity",
            x=data["timestamp"], y=data["humidity"],
            hovertemplate = "<b>%{y:.0f}" + HUMIDITY_UNIT + "</b>",
            line = dict(color = raw_humidity_color, width = raw_line_width)
            ), 
        secondary_y = True,
        row=1, col=1
        )

    if SHOW_FILTERED_DATA:
        fig.add_trace(
            go.Scatter(
                name = "Temperature (filtered)",
                x=data["timestamp"], y=data["temperature_filtered"],
                hovertemplate = "<b>%{y:.1f}" + TEMPERATURE_UNIT + "</b>",
                line = dict(color = TEMPERATURE_PRIMARY_COLOR, width = PLOT_PRIMARY_LINE_WIDTH)
                ), 
            secondary_y = False,
            row=1, col=1
            )

        fig.add_trace(
            go.Scatter(
                name = "Humidity (filtered)",
                x=data["timestamp"], y=data["humidity_filtered"],
                hovertemplate = "<b>%{y:.0f}" + HUMIDITY_UNIT + "</b>",
                line = dict(color = HUMIDITY_PRIMARY_COLOR, width = PLOT_PRIMARY_LINE_WIDTH)
                ), 
            secondary_y = True,
            row=1, col=1
            )

    fig.update_layout(
        hovermode = "x unified",
        )

    fig.update_xaxes(
        title_text = "Time",
        showline = True,
        linewidth = 2,
        linecolor = 'black',
        rangeslider_visible = True,
        rangeselector = dict(
            buttons = list([
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=3, label="3d", step="day", stepmode="backward"),
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(count=14, label="2w", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=2, label="2m", step="month", stepmode="backward"),
                dict(step="all")
                ])
            )
        )

    fig.update_yaxes(
        title_text=f"Temperature [{TEMPERATURE_UNIT}]", 
        secondary_y=False,
        color = TEMPERATURE_PRIMARY_COLOR,
        gridcolor = TEMPERATURE_PRIMARY_COLOR,
        linecolor = 'black',
        showgrid = False,
        showline = True,
        linewidth = 2,
        )

    fig.update_yaxes(
        title_text=f"Humidity [{HUMIDITY_UNIT}]", 
        secondary_y=True,
        color = HUMIDITY_PRIMARY_COLOR,
        gridcolor = HUMIDITY_PRIMARY_COLOR,
        linecolor = 'black',
        showgrid = False,
        showline = True,
        linewidth = 2,
        )

    fig.update_layout(
        legend = dict(
            orientation = "h",
            yanchor = "bottom",
            y = 1.02,
            xanchor = "right",
            x = 0.95
            ),
        height = PLOT_HEIGHT,
        )

    return fig

app = Dash(__name__)

app.layout = html.Div(style={'color': '#333333', 'font-family': 'Calibri', 'textAlign': 'center'}, children=[
    html.H1('Project X'),
    dcc.Graph(
        id = "inner-sensor",
        figure = create_figure()
    ),
    dcc.Interval(
        id = "interval",
        interval = REFRESH_INTERVAL,
        n_intervals = 0
    ),
])

@app.callback(Output("inner-sensor", "figure"),
        [Input("interval", "n_intervals")])
def update_plot_callback(n_intervals):
    return create_figure()

if __name__ == '__main__':
    app.run_server(host = SERVER_IP, port = SERVER_PORT)