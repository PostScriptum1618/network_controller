import time
from pathlib import Path
from dash import html
from jupyter_dash import JupyterDash
from dash import dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import pandas as pd
from threading import Thread
import os
from shutil import rmtree
import main


def read_servers_file(file_path):
    with open(file_path, 'r') as servers_file:
        return [server.strip() for server in servers_file]


def read_ttls_file(file_path):
    with open(file_path, 'r') as ttl_file:
        return [float(row.strip()) for row in ttl_file]

def make_ttls_files(servers_path, servers_ttls_path):
    servers = read_servers_file(servers_path)
    for server in servers:
        ttl_file_path = servers_ttls_path / f'{server}_ttls.log'
        if not ttl_file_path.exists():
            ttl_file_path.touch()
def read_data():
    pwd = Path(__file__).parent
    servers_ttls = pwd / 'servers_ttls'
    data = {}
    for server_file in (pwd / 'servers.txt').read_text().splitlines():
        server = server_file.strip()
        data[server] = read_ttls_file(servers_ttls / f'{server}_ttls.log')
    return data


def setup_dirs():
    pwd = Path(__file__).parent
    hosts_path = pwd / 'hosts.txt'
    servers_path = pwd / 'servers.txt'
    servers_ttls_path = pwd / 'servers_ttls'

    if not hosts_path.exists():
        print("hosts.txt file not found!!!")

    if not servers_path.exists():
        print('servers.txt not found')
    elif servers_ttls_path.exists():
        rmtree(servers_ttls_path)

    os.mkdir(servers_ttls_path)
    servers = read_servers_file(servers_path)
    if servers_ttls_path.exists():
            make_ttls_files(servers_path, servers_ttls_path)

app = JupyterDash(__name__)


@app.callback(
    Output("heatmap", "figure"),
    Input("animateInterval", "n_intervals"),
    State("heatmap", "figure")
)
def update_graph(i, fig):
    global data
    data = read_data()
    servers = list(data.keys())
    fig = go.Figure()

    for server, ttls in data.items():
        fig.add_trace(
            go.Scatter(
                x=list(range(1, len(ttls) + 1)),
                y=ttls,
                name=f'TTL до {server}',
                mode='lines+markers',
                opacity=0.8,
                line={'width': 3}
            )
        )

    fig.update_layout(
        title_text='TTL до серверов',
        title_font_size=16,
        plot_bgcolor='rgba(0,0,0,0.05)',
        autosize=True
    )

    return fig


@app.callback(
    Output("heatmap1", "figure"),
    Input("animateInterval1", "n_intervals"),
    State("heatmap1", "figure")
)
def update_table(i, fig):
    df = pd.read_csv('status.csv', sep='|')
    total_height = len(df["Hosts"]) * 60
    tab = go.Figure(data=go.Table(
        header=dict(values=['Hosts', 'Status']),
        cells=dict(values=[df['Hosts'], df['Status']])
    ))
    tab.update_layout(height=total_height)
    return tab


if __name__ == '__main__':
    setup_dirs()
    hosts, servers, servers_ttls, df, param = main.make_vars()
    thread1 = Thread(target=main.check_ping, args=[hosts, servers, servers_ttls, df, param], daemon=True)
    thread2 = Thread(target=app.run_server, kwargs={'mode': 'inline'}, daemon=True)

    app.layout = html.Div(
        [
            dcc.Graph(id="heatmap"),
            dcc.Interval(id="animateInterval", interval=300, n_intervals=0),
            dcc.Graph(id="heatmap1"),
            dcc.Interval(id="animateInterval1", interval=300, n_intervals=0),
        ]
    )

    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
