from plotly.subplots import make_subplots
import utilizations


def make_details(host, user, secret):
    # hosts = inventory['Hosts']
    # users = inventory['Users']
    # passwords = inventory['Passwords']
    # figures = {}
    # for h, host in enumerate(inventory['Hosts']):
    #     user = str(inventory['Users'][h])
    #     secret = str(inventory['Passwords'][h])
    print('trying to connect', host)
    try:
        cpu, mem = utilizations.get_stat(host, user, secret)

        fig = make_subplots(rows=2, cols=2,
                            subplot_titles=('CPU Utilization', 'Memory Utilization', 'Details'),
                            specs=[[{"type": "xy"}, {"type": "domain"}],
                                   [{"type": "table"}, {}]])
        fig.add_bar(row=1, col=1, x=['last 1 min', 'last 5 min', 'last 15 min'], y=cpu['load_average'])
        fig.add_pie(row=1, col=2, values=list(mem.values())[-2:], labels=['Used', "Free"], hole=0.5, legendwidth=40,
                    textposition='inside')

        cput = dict(cpu)
        cput['load_average'] = cpu['load_average'][0]
        # cpu_df = pd.DataFrame(cput, index=[0])
        fig.add_table(row=2, col=1, header=dict(values=['System Time', 'Up Time', 'Users', '1 Minute Load']),
                      cells=dict(values=list(cput.values())))
        fig.update_layout(title=f'{host} Utilization Details', showlegend=False)

        return fig
    except TypeError as e:
        print(e)
