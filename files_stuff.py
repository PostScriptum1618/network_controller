import pandas as pd
from pathlib import Path
from os import mkdir
from shutil import rmtree


def read_inventory_file(file_path):
    inventory = pd.read_csv(file_path, sep='|', index_col=[0])
    return inventory


def read_servers(inventory_path):
    hosts = read_inventory_file(inventory_path)['Hosts']
    inventory = read_inventory_file(inventory_path)
    servers = []
    for h, host in enumerate(hosts):
        if inventory['Role'][h] == 'server':
            servers.append(hosts[h])
    return servers


def read_hosts(inventory_path):
    hosts = list(read_inventory_file(inventory_path)['Hosts'])
    return hosts


def read_ttls_file(file_path):
    with open(file_path, 'r') as ttl_file:
        return [float(row.strip()) for row in ttl_file]


def make_ttls_files(inventory_path, servers_ttls_path):
    roles = read_inventory_file(inventory_path)['Role']
    hosts = read_hosts(inventory_path)
    servers = []
    for h, host in enumerate(hosts):
        if roles[h] == 'server':
            servers.append(host)
    print(servers)
    for server in servers:
        ttl_file_path = servers_ttls_path / f'{server}_ttls.log'
        if not ttl_file_path.exists():
            ttl_file_path.touch()


def setup_dirs():
    pwd = Path(__file__).parent
    inventory_path = pwd / 'inventory.csv'
    servers_ttls_path = pwd / 'servers_ttls'
    status_path = pwd / 'status.csv'

    if not inventory_path.exists():
        print("inventory.csv file not found!!!, Making the template...")
        inventory = pd.DataFrame({'Role': None, 'Hosts': None, 'Users': None, 'Passwords': None}, index=[0])
        inventory.to_csv('inventory.csv', sep='|')
        print('Fill inventory.csv')
    if servers_ttls_path.exists():
        rmtree(servers_ttls_path)
    mkdir(servers_ttls_path)
    make_ttls_files(inventory_path, servers_ttls_path)

    inventory = read_inventory_file(inventory_path)
    hosts = inventory['Hosts']
    df = pd.DataFrame({'Hosts': hosts, 'Status': [None] * len(hosts)})
    if not status_path.exists():
        df.to_csv('status.csv', sep='|')
