import pandas as pd
import plotly.express as px
from constants import *
from dash import Dash, Input, Output, callback, dcc, html

datafile = os.path.join(REPOSITORY_PATH, "out", "events.csv")
df = pd.read_csv(datafile)

app = Dash()

# Requires Dash 2.17.0 or later
app.layout = [
    html.H1(children="Session information", style={"textAlign": "center"}),
    dcc.Dropdown(df.type.unique(), "ot", id="dropdown-selection"),
    dcc.Graph(id="graph-content"),
]


@callback(Output("graph-content", "figure"), Input("dropdown-selection", "value"))
def update_graph(value):
    dff = df[df.type == value]
    dff.reset_index(inplace=True)  # to have index accessible as a normal column

    # use x="index" if you want just enumerated ladtists plotted
    return px.scatter(dff, x="time", y="min_lat_dist", hover_data="min_lat_dist", color="min_lat_dist")


if __name__ == "__main__":
    app.run(debug=True)
