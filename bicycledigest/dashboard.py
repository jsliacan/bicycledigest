import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from constants import *
from dash import Dash, Input, Output, callback, dcc, html

datafile = os.path.join(REPOSITORY_PATH, "out", "events.csv")
df = pd.read_csv(datafile)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Requires Dash 2.17.0 or later
app.layout = [
    dbc.Row(
        [
            html.H1(children="Session information", style={"textAlign": "center"}),
            dcc.Dropdown(df.type.unique(), "ot", id="dropdown-selection"),
        ]
    ),
    dbc.Row(
        [
            dcc.Graph(id="map-lidar"),
        ]
    ),
    dbc.Row(
        [
            dbc.Col(dcc.Graph(id="histogram-lidar")),
            dbc.Col(html.H2(children="Placeholder", style={"textAlign": "center"})),
        ]
    ),
]


@callback(Output("map-lidar", "figure"), Input("dropdown-selection", "value"))
def update_lidar_map(value):
    dff = df[df.type == value]
    dff.reset_index(inplace=True)  # to have index accessible as a normal column

    # use x="index" if you want just enumerated ladtists plotted
    fig = px.scatter_map(
        df,
        lat="gps_lat",
        lon="gps_lon",
        color="latdist_min",
        size="latdist_min",
        color_continuous_scale="solar",
        size_max=10,
        zoom=10,
        hover_name="hash",
        hover_data=["road_ref", "road_lanes", "road_maxspeed", "road_width", "road_oneway"],
        title="Overtakes",
    )

    return fig


@callback(Output("histogram-lidar", "figure"), Input("dropdown-selection", "value"))
def update_lidar_histogram(value):
    dff = df[df.type == value]
    dff.reset_index(inplace=True)  # to have index accessible as a normal column

    # use x="index" if you want just enumerated ladtists plotted
    fig = px.histogram(df, x="latdist_min", title="Lateral distances")

    return fig


if __name__ == "__main__":
    app.run(debug=True)
