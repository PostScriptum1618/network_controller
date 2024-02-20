from pathlib import Path
from dash import html
from jupyter_dash import JupyterDash
from dash import dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import pandas as pd
from threading import Thread

import main
from files_stuff import read_ttls_file, setup_dirs, read_servers, read_inventory_file
from utils_app import make_details


def read_data():
    pwd = Path(__file__).parent
    servers_ttls = pwd / 'servers_ttls'
    inventory_path = pwd / 'inventory.csv'
    data = {}
    servers = read_servers(inventory_path)
    for server in servers:
        data[server] = read_ttls_file(servers_ttls / f'{server}_ttls.log')
    return data


app = JupyterDash(__name__, use_pages=False)


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
                name=f'Delay to {server}',
                mode='lines+markers',
                opacity=0.8,
                line={'width': 3}
            )
        )

    fig.update_layout(
        title_text='Delay to Servers',
        title_font_size=16,
        autosize=True,
        overwrite=True
    )

    return fig


@app.callback(
    Output("heatmap1", "figure"),
    Input("animateInterval1", "n_intervals"),
    State("heatmap1", "figure")
)
def update_table(i, fig):
    df = pd.read_csv('status.csv', sep='|', index_col=0)
    total_height = len(list(df["Hosts"])) * 90
    colors = []
    for row in list(df['Status']):
        if 'ERROR' in str(row):
            colors.append('#FF0000')
        elif 'TIMEOUT' in str(row):
            colors.append('#FFFF00')
        elif 'delay' in str(row):
            colors.append('#109010')

    tab = go.Figure(data=go.Table(
        header=dict(values=['Hosts', 'Status'],
                    line_color='rgba(0, 0, 0, 0.75)', ),
        cells=dict(values=list([list(df['Hosts']), list(df['Status'])]),
                   line_color='rgba(0, 0, 0, 0.75)',
                   fill_color=[colors]
                   ),

    ))

    tab.update_layout(height=total_height)
    return tab


@app.callback(
    Output("utilmap", "figure"),
    Input("animateInterval2", "n_intervals"),
    Input('dropdown', 'value'),
    State("utilmap", "figure")
)
def update_plot(i, value, fig):
    pwd = Path(__file__).parent
    inventory_path = pwd / 'inventory.csv'
    inventory = read_inventory_file(inventory_path)
    hdf = pd.DataFrame(inventory.loc[inventory['Hosts'].isin([value])])
    user = str(hdf['Users'].values[0])
    host = str(hdf['Hosts'].values[0])
    passwd = str(hdf['Passwords'].values[0])
    figure = make_details(host, user, passwd)
    return figure


if __name__ == '__main__':
    setup_dirs()
    hosts, servers, servers_ttls, df = main.make_vars()
    data = read_data()
    thread1 = Thread(target=main.check_ping, args=[hosts, servers, servers_ttls, df], daemon=True)
    thread2 = Thread(target=app.run_server, kwargs={'mode': 'inline'}, daemon=True)

    app.layout = html.Div(
        [
            dcc.Graph(id="heatmap"),
            dcc.Interval(id="animateInterval", interval=300, n_intervals=0),
            dcc.Graph(id="heatmap1", ),
            dcc.Interval(id="animateInterval1", interval=300, n_intervals=0),
            dcc.Dropdown(
                options=servers,
                placeholder="Select a server",
                clearable=False,
                id='dropdown',
            ),
            dcc.Graph(id="utilmap"),
            dcc.Interval(id="animateInterval2", interval=300, n_intervals=0)
        ]

    )

    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
