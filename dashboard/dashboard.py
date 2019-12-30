import os
import re
import glob

import numpy as np
import pandas as pd

from multiprocessing import Manager

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


SCORES_DIR = os.getenv("DASHBOARD_SCORES_DIR", "./results")


def init_dashborad():
    os.makedirs(SCORES_DIR, exist_ok=True)
    if not os.path.exists(os.path.join(SCORES_DIR, "scores.csv")):
        df_scores_blank = pd.DataFrame([["boston_house_prices_train", 6.303904029016756],
                                        ["boston_house_prices_val", 7.554702970297035]],
                                       columns=["file", "baseline"])
        df_scores_blank.to_csv(os.path.join(SCORES_DIR, "scores.csv"), index=False)


init_dashborad()

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

df_scores = pd.read_csv(os.path.join(SCORES_DIR, "scores.csv"))[["file", "baseline"]]

df_list = []
full_model_list = []

manager = Manager()
lock = manager.Lock()


def update_table(lock):

    lock.acquire()

    df_path_list = glob.glob(os.path.join(SCORES_DIR, "*.csv"))
    df_path_list.sort(key=os.path.getmtime)

    for df_path in df_path_list:
        if "scores.csv" not in df_path:
            model_id = df_path.split("/")[-1].strip(".csv")
            if model_id not in full_model_list:
                df_temp = pd.read_csv(df_path)[["mae"]]
                df_temp.columns = ["model_" + model_id]
                full_model_list.append(model_id)
                df_list.append(df_temp)

    lock.release()


def cell_style(value, threshold_value):
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
    return html.Div([
        html.H4(children="Metric by file"),
        generate_table()
    ])


def serve_graph_layout(default="boston_house_prices_val"):
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


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content")
])


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


if __name__ == "__main__":
    app.run_server(debug=False, port=7050, host="0.0.0.0")
