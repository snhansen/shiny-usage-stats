import sqlite3
import os
import plotly.express as px
import plotly.io as pio
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import functools

DATABASE_PATH = ""
DATABASE_FILE = "shiny_database.sqlite"


def temporary_cache(fn=None, *, ttl=60):
    if fn is None:
        return functools.partial(temporary_cache, ttl=ttl)

    cache = None
    cache_time = datetime.fromordinal(1)

    @functools.wraps(fn)
    def inner(*args, **kwargs):
        nonlocal cache, cache_time
        now = datetime.now()
        if ttl < (now - cache_time).total_seconds():
            cache = fn(*args, **kwargs)
            cache_time = now
        return cache
    return inner


def load_data():
        db = sqlite3.connect(f"{DATABASE_PATH}{DATABASE_FILE}")
        cursor = db.cursor()
        cursor.execute("SELECT * FROM session")
        usage_data = cursor.fetchall()
        return usage_data


def parse_data(data):
        parsed_data = []
        for line in data:
                app, user, t1, sid, t2, info, *_ = line
                t1, _ = t1.split('+')
                t1 = datetime.strptime(t1, "%Y-%m-%d %H:%M:%S.%f").replace(microsecond = 0)
                t2, _ = t2.split('+')
                t2 = datetime.strptime(t2, "%Y-%m-%d %H:%M:%S.%f").replace(microsecond = 0)
                parsed_data.append((app, user, t1, t2, info, sid))

        return pd.DataFrame(parsed_data, columns=["app", "user", "connect", "disconnect", "user_agent", "session_id"])


@temporary_cache(ttl=3600)
def get_data():
        sql_data = load_data()
        return parse_data(sql_data)


def plot_hourly_connections(data, appname, period = None):
        data = data.set_index("connect")
        data = data[data.app == appname]
        user = data.user.values[0]
        if data.empty:
                plot_data = pd.DataFrame()
                plot_data["connect"] = period
                plot_data["n"] = [0, 0]
                plot_data = plot_data.set_index("connect")
                plot = px.bar(plot_data, y = "n", labels = {"connect": "Hour", "n": "Connections"})
                plot.update_layout(title_text=f"Hourly connections for {appname} ({user})", title_x = 0.5)
                plot.update_xaxes(range = period)
                plot.update_yaxes(range = [0, 1])
                return plot
        else:
                plot_data = data.groupby([data.index.year, data.index.month, data.index.day, data.index.hour]).size()
                plot_data.index = plot_data.index.set_names(["year", "month", "day", "hour"])
                plot_data = plot_data.reset_index().rename(columns = {0: "n"})
                plot_data["connect"] = plot_data.apply(lambda x: datetime(x.year, x.month, x.day, x.hour), axis = 1)
                plot_data = plot_data.set_index("connect")
                plot = px.bar(plot_data, y = "n", labels = {"connect": "Hour", "n": "Connections"})
                plot.update_layout(title_text=f"Hourly connections for {appname} ({user})", title_x = 0.5)
                plot.update_traces(width = 1000*60*60, offset = 0)
                plot.update_xaxes(range = period)
                return plot


def plot_daily_connections(data, appname, period = None):
        data = data.set_index("connect")
        data = data[data.app == appname]
        user = data.user.values[0]
        if data.empty:
                plot_data = pd.DataFrame()
                plot_data["connect"] = period
                plot_data["n"] = [0, 0]
                plot_data = plot_data.set_index("connect")
                plot = px.bar(plot_data, y = "n", labels = {"connect": "Day", "n": "Connections"})
                plot.update_layout(title_text=f"Daily connections for {appname} ({user})", title_x = 0.5)
                plot.update_xaxes(range = period)
                plot.update_yaxes(range = [0, 1])
                return plot
        else:        
                plot_data = data.groupby([data.index.year, data.index.month, data.index.day]).size()
                plot_data.index = plot_data.index.set_names(["year", "month", "day"])
                plot_data = plot_data.reset_index().rename(columns = {0: "n"})
                plot_data["connect"] = plot_data.apply(lambda x: datetime(x.year, x.month, x.day), axis = 1)
                plot_data = plot_data.set_index("connect")
                plot = px.bar(plot_data, y = "n", labels = {"connect": "Day", "n": "Connections"})
                plot.update_layout(title_text=f"Daily connections for {appname} ({user})", title_x=0.5)
                plot.update_traces(width = 1000*60*60*24, offset = 0)
                plot.update_xaxes(range = period)
                return plot


def plot_monthly_connections(data, appname, period = None):
        data = data.set_index("connect")
        data = data[data.app == appname]
        user = data.user.values[0]
        if data.empty:
                plot_data = pd.DataFrame()
                plot_data["connect"] = period
                plot_data["n"] = [0, 0]
                plot_data = plot_data.set_index("connect")
                plot = px.bar(plot_data, y = "n", labels = {"connect": "Month", "n": "Connections"})
                plot.update_layout(title_text=f"Monthly connections for {appname} ({user})", title_x = 0.5)
                plot.update_xaxes(range = period)
                plot.update_yaxes(range = [0, 1])
                return plot
        else:        
                plot_data = data.groupby([data.index.year, data.index.month]).size()
                plot_data.index = plot_data.index.set_names(["year", "month"])
                plot_data = plot_data.reset_index().rename(columns = {0: "n"})
                plot_data["connect"] = plot_data.apply(lambda x: datetime(x.year, x.month, 1), axis = 1)
                plot_data = plot_data.set_index("connect")
                plot = px.bar(plot_data, y = "n", labels = {"connect": "Month", "n": "Connections"})
                plot.update_traces(width = 1000*60*60*24*30, offset = 0)
                plot.update_xaxes(range = period)
                plot.update_layout(title_text=f"Monthly connections for {appname} ({user})", title_x=0.5)
                return plot


pio.templates.default = "plotly_white"
data = get_data()
apps = data.groupby("user")["app"].apply(lambda x: list(np.unique(x))).to_dict()

app = Dash(__name__, external_stylesheets = [dbc.themes.FLATLY], url_base_pathname = "/shinystats/")

app.layout = html.Div(
        [
                dbc.Row(children = [
                        html.H1("Shiny stats", style={'textAlign': 'center'}),
                        html.Br(),
                        dbc.Col(children = [
                                html.H5("Pick user"),
                                dcc.Dropdown(
                                        id = "user",
                                        options = list(apps.keys()),
                                        value = "stefan"
                                )
                        ]),
                        dbc.Col(children = [
                                html.H5("Pick app"),
                                dcc.Dropdown(
                                        id = "app",
                                        options = apps["stefan"],
                                        value = "measurementerror"
                                )
                        ]),
                ]),
                dbc.Row(
                        dbc.Col(children = [
                                html.Br(),
                                html.Div(children = [
                                        dcc.Graph(
                                                id = "hourly_plot"
                                        ),
                                        dcc.Graph(
                                                id = "daily_plot"
                                        ),
                                        dcc.Graph(
                                                id = "monthly_plot"
                                        )
                                        ],
                                        style={"textAlign": "center"}
                                )]
                        )
                )],
        className = "container"
)


@app.callback(
        Output("app", "options"),
        Input("user", "value"))
def set_users_apps(selected_user):
        data = get_data()
        apps = data.groupby("user")["app"].apply(lambda x: list(np.unique(x))).to_dict()
        return apps[selected_user]


@app.callback(
        Output("hourly_plot", "figure"),
        Input("app", "value"))
def update_hourly_plot(app):
        data = get_data()
        upper = datetime.today() + timedelta(hours = 1)
        upper.replace(minute = 0 , second = 0, microsecond = 0)
        lower = upper - timedelta(days = 2)
        return plot_hourly_connections(data, app, period = [lower, upper])


@app.callback(
        Output("daily_plot", "figure"),
        Input("app", "value"))
def update_daily_plot(app):
        data = get_data()
        upper = datetime.today() + timedelta(days = 1)
        lower = upper - timedelta(days = 30)
        return plot_daily_connections(data, app, period = [lower, upper])


@app.callback(
        Output("monthly_plot", "figure"),
        Input("app", "value"))
def update_monthly_plot(app):
        data = get_data()
        upper = datetime.today() + timedelta(days = 1)
        lower = upper - timedelta(days = 365)
        return plot_monthly_connections(data, app, period = [lower, upper])


if __name__ == "__main__":
    app.run_server(debug=False)