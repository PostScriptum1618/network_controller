import datetime
import time
import pandas as pd
from threading import Thread
from pathlib import Path
import ping3

from files_stuff import read_servers, read_hosts


def overfill_check(servers, servers_ttls):
    for server in servers:
        log_file = Path(servers_ttls) / f"{server}_ttls.log"
        if log_file.exists() and log_file.stat().st_size >= 10:
            with open(log_file, "r+") as file:
                lines = file.readlines()
                lines = lines[-10:]  # Keep only the last 10 lines
                file.seek(0)
                file.writelines(lines)
                file.truncate()


def make_vars():
    print('Checking ping...')
    pwd = Path(__file__).resolve().parent
    servers_ttls = pwd / 'servers_ttls'
    inventory_path = pwd / 'inventory.csv'

    servers = read_servers(inventory_path)

    hosts = read_hosts(inventory_path)

    df = pd.DataFrame({'Hosts': hosts, 'Status': [None] * len(hosts)})

    return hosts, servers, servers_ttls, df


def check_ping(hosts, servers, servers_ttls, df, wait_time=0.2):
    while True:
        for h, host in enumerate(hosts):
            response = ping3.ping(host, seq=1, timeout=wait_time)
            if (response is not None) and (response is not False):
                # print(f"{host}: Host Active")
                df.at[h, 'Status'] = f'delay is {response}'
                print(f'delay is {response}')
                if host in servers:
                    with open(servers_ttls / f'{host}_ttls.log', "a+") as ttl_file:
                        ttl_file.write(f"{response:.4f}\n")
            elif (response is None) and ('TIMEOUT' not in str(df.at[h, 'Status'])):
                df.at[h, 'Status'] = f'TIMEOUT since {datetime.datetime.now()}'
                if host in servers:
                    with open(servers_ttls / f'{host}_ttls.log', "a+") as ttl_file:
                        ttl_file.write(f"{-1}\n")
            elif (response is False) and ('ERROR' not in str(df.at[h, 'Status'])):
                df.at[h, 'Status'] = f'ERROR since {datetime.datetime.now()}'
                if host in servers:
                    with open(servers_ttls / f'{host}_ttls.log', "a+") as ttl_file:
                        ttl_file.write(f"{-1}\n")

        df.to_csv('status.csv', encoding='utf-8', sep='|')
        overfill_check(servers, servers_ttls)
        print("====END OF SCAN ROUND====")
        time.sleep(5)


if __name__ == '__main__':
    hosts, servers, servers_ttls, df = make_vars()

    thread1 = Thread(target=check_ping, args=(hosts, servers, servers_ttls, df))
    thread1.start()

    # Add code for the Dash app...
