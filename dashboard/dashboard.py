import os
import re
import glob

import pandas as pd

from multiprocessing import Manager

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


# path to the folder where metric files are stored
SCORES_DIR = os.getenv("DASHBOARD_SCORES_DIR", "./results")

# dataframe which will store scores in RAM
df_scores = pd.DataFrame([["boston_house_prices_train", 6.303904029016756],
                          ["boston_house_prices_val", 7.554702970297035]],
                         columns=["file", "baseline"])

# list of dataframes with metrics
df_list = []
# list of model names
full_model_list = []

# lock manager to update the table and the graph properly when new files arrives
manager = Manager()
lock = manager.Lock()


def update_table(lock):
    """ Updates the data for table of results when the new metrics file arrives. """

    lock.acquire()

    # get list of all metrics files
    df_path_list = glob.glob(os.path.join(SCORES_DIR, "*.csv"))
    df_path_list.sort(key=os.path.getmtime)

    for df_path in df_path_list:
        model_id = df_path.split("/")[-1].strip(".csv")
        if model_id not in full_model_list:
            # add to lists if there is new file
            df_temp = pd.read_csv(df_path)[["mae"]]
            df_temp.columns = ["model_" + model_id]
            full_model_list.append(model_id)
            df_list.append(df_temp)

    lock.release()


def cell_style(value, threshold_value):
    """ Paints row to green or red depending on the threshold value. """

    if value <= threshold_value:
        style = {
            "backgroundColor": "#e6ffef",
        }
    else:
        style = {
            "backgroundColor": "#ffe6e6",
        }
    return style


def generate_table():
    """ Generates new HTML page with dashboard table of results when the new metrics file arrives. """

    update_table(lock)

    df = pd.concat([df_scores] + list(df_list)[-5:], axis=1).round(2)

    body = []
    for i in range(len(df)):
        row = []
        style = cell_style(df.iloc[i][df.columns[-1]], df.iloc[i]["baseline"])
        for col in df.columns:
            if col == "file":
                val = html.Td(dcc.Link(df.iloc[i][col], href=f"/graph/{df.iloc[i]['file']}"), style=style)
            else:
                val = html.Td(df.iloc[i][col], style=style)
            row.append(val)
        row = html.Tr(row)
        body.append(row)

    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in df.columns])] +

        # Body
        body
    )


def serve_dashboard_layout():
    """ Serves HTML page with table of results. """

    return html.Div([
        html.H4(children="Metric by file"),
        generate_table()
    ])


def serve_graph_layout(default="boston_house_prices_val"):
    """ Serves HTML pages with graph of metric evolution. """

    update_table(lock)
    xaxisrange = list(range(1, len(df_list) + 1))
    df = pd.concat([df_scores[["file"]]] + df_list, axis=1)
    df.set_index("file", drop=True, inplace=True)
    return html.Div([
        html.Div([
            dcc.Graph(
                id="quality-graph",
                figure={
                    "data": [
                        {
                            "x": xaxisrange,
                            "y": df.loc[default],
                            "name": "Current score"
                        },
                        {
                            "x": xaxisrange,
                            "y": [df_scores[df_scores["file"] == default].iloc[0]["baseline"]] * len(xaxisrange),
                            "mode": "lines",
                            "name": "Baseline score"
                        }
                    ],
                    "layout": dict(
                        autosize=True,
                        hovermode="closest",
                        title=f"Metrics history for file {default}",
                        xaxis={"title": "Model",
                               "ticktext": list(df.columns),
                               "tickvals": list(range(1, len(df.loc[default]) + 1)),
                               "tickangle": -90,
                               "automargin": True},
                        yaxis={"title": "MAE"}
                    )
                },
                style={"height": "80vh"}
            )
        ]
        ),
        html.Div([
            dcc.Dropdown(
                id="dist-drop",
                options=[{"label": ind, "value": ind} for ind in df.index],
                value=default)
        ]
        ),
        html.Br(),
        dcc.Link("Go to dashboard", href="/dashboard"),
    ])


# create Dash web-application
app = dash.Dash(__name__, external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"])

app.config.suppress_callback_exceptions = True

# create app layout
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content")
])


# create dropdown menu for switching between graphs
@app.callback(
    Output(component_id="quality-graph", component_property="figure"),
    [Input(component_id="dist-drop", component_property="value")]
)
def update_graph(value):
    xaxisrange = list(range(1, len(df_list) + 1))
    df = pd.concat([df_scores[["file"]]] + df_list, axis=1)
    df.set_index("file", drop=True, inplace=True)
    return {
                "data": [
                    {
                        "x": xaxisrange,
                        "y": df.loc[value],
                        "name": "Current score"
                    },
                    {
                        "x": xaxisrange,
                        "y": [df_scores[df_scores["file"] == value].iloc[0]["baseline"]] * len(xaxisrange),
                        "mode": "lines",
                        "name": "Baseline score"
                    }
                ],
                "layout": dict(
                    autosize=True,
                    hovermode="closest",
                    title=f"Metrics history for file {value}",
                    xaxis={"title": "Model",
                           "ticktext": list(df.columns),
                           "tickvals": list(range(1, len(df.loc[value]) + 1)),
                           "tickangle": -90,
                           "automargin": True},
                    yaxis={"title": "MAE"}
                )
            }


# callback to distinguish between different HTML "pages" with content
@app.callback(dash.dependencies.Output("page-content", "children"),
              [dash.dependencies.Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/graph":
        return serve_graph_layout()
    elif re.search("\/graph\/[\d\w]+", str(pathname)):
        return serve_graph_layout(str(pathname).split("/")[-1])
    elif pathname == "/dashboard":
        return serve_dashboard_layout()
    else:
        return serve_dashboard_layout()


# run app
if __name__ == "__main__":
    app.run_server(debug=False, port=7050, host="0.0.0.0")
