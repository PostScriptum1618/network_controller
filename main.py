import datetime
import os
import platform
import time
import pandas as pd
from multiprocessing import Process
from threading import Thread
from pathlib import Path
import subprocess
import ping3



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

    with open(pwd / "servers.txt", 'r') as servers_file:
        servers = [server.strip() for server in servers_file.readlines()]

    with open(pwd / "hosts.txt", "r", encoding="utf-8") as hosts_file:
        hosts = [host.strip() for host in hosts_file.readlines()]

    df = pd.DataFrame({'Hosts': hosts, 'Status': [None] * len(hosts)})
    param = '-n' if platform.system().lower() == 'windows' else '-c'

    return hosts, servers, servers_ttls, df, param


def check_ping(hosts, servers, servers_ttls, df, param):
    while True:
        for h, host in enumerate(hosts):
            t1 = time.time()

            response = ping3.ping(host, seq=1)
            ttl = time.time() - t1
            # if host in servers:
            #     with open(servers_ttls / f'{host}_ttls.log', "a+") as ttl_file:
            #         ttl_file.write(f"{ttl:.4f}\n")

            if (response != None) and (response != False):
                #print(f"{host}: Host Active")
                df.at[h, 'Status'] = f'delay is {str(response)}'
                if host in servers:
                    with open(servers_ttls / f'{host}_ttls.log', "a+") as ttl_file:
                        ttl_file.write(f"{response:.4f}\n")
            elif response == None and (df.at[h, 'Status'] != 'Timeout'):
                df.at[h, 'Status'] = f'TIMEOUT since {datetime.datetime.now()}'
                if host in servers:
                    with open(servers_ttls / f'{host}_ttls.log', "a+") as ttl_file:
                        ttl_file.write(f"{-1}\n")
            elif response == False and (df.at[h, 'Status'] != 'Error'):
                df.at[h, 'Status'] = f'ERROR since {datetime.datetime.now()}'
                if host in servers:
                    with open(servers_ttls / f'{host}_ttls.log', "a+") as ttl_file:
                        ttl_file.write(f"{-1}\n")

        df.to_csv('status.csv', encoding='utf-8', sep='|')
        overfill_check(servers, servers_ttls)
        print("====END OF SCAN ROUND====")
        time.sleep(5)


if __name__ == '__main__':
    hosts, servers, servers_ttls, df, param = make_vars()

    thread1 = Thread(target=check_ping, args=(hosts, servers, servers_ttls, df, param), daemon=True)
    thread1.start()

    # Add code for the Dash app...
