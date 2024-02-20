import paramiko


def get_stat(host, username, password, port=22):
    data = []
    cpu = {}
    load = []
    mem = {}
    gtos = []
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=username, password=password, port=port)
        stdin, stdout, stderr = client.exec_command('uname')
        gtos.append(stdout.read() + stderr.read())
        if b'Linux\n' in gtos:
            # Unix
            print('conn to lin')
            stdin, stdout, stderr = client.exec_command('uptime')
            data.append(stdout.read() + stderr.read())
            stdin, stdout, stderr = client.exec_command('free -t -m')
            data.append(stdout.readlines() + stderr.readlines())
            client.close()
            cpu['system_time'] = data[0].split()[0].decode("utf-8")
            cpu['up_time'] = data[0].split()[2].decode("utf-8").replace(',', '')
            cpu['users'] = str(data[0].split()[4].decode("utf-8"))
            for letter in data[0].split()[-3:]:
                if letter.decode("utf-8") != ', ':
                    load.append(str(letter.decode("utf-8")[:4].replace(',', '.')))
            cpu['load_average'] = load
            mem['total'] = str(data[1][1].split()[1])
            mem['used'] = str(data[1][1].split()[2])
            mem['free'] = str(data[1][1].split()[3])
            return cpu, mem
        else:
            # windows
            print('conn to win')
            stdin, stdout, stderr = client.exec_command('chcp 65001')
            stdin, stdout, stderr = client.exec_command('wmic cpu get loadpercentage')
            data.append(stdout.read() + stderr.read())
            cpu_load = data[0].split()[1].decode("utf-8")
            data = []
            stdin, stdout, stderr = client.exec_command('systeminfo | find "Total Physical Memory"')
            data.append(stdout.read() + stderr.read())
            mem_total = data[0].split()[3].decode('utf-8')
            mem_total = int(str(mem_total).replace('\xa0', ''))
            data = []
            stdin, stdout, stderr = client.exec_command('systeminfo | find "Available Physical Memory:"')
            data.append(stdout.read() + stderr.read())
            mem_aval = data[0].split()[3].decode('utf-8')
            mem_aval = int(str(mem_aval).replace('\xa0', ''))
            mem_inuse = mem_total - mem_aval
            data = []
            stdin, stdout, stderr = client.exec_command('systeminfo | find "System Boot Time:"')
            data.append(stdout.read() + stderr.read())
            boot_time = (data[0].split()[3:5])
            boot = []
            [boot.append(row.decode('utf-8')) for row in boot_time]
            boot_time = ' '.join(boot)
            client.close()
            mem = {}
            mem['total'] = mem_total
            mem['used'] = mem_inuse
            mem['free'] = mem_aval

            cpu = {}
            cpu['system_time'] = 'Windows dont support'
            cpu['up_time'] = f'Is up since {boot_time}'
            cpu['users'] = 1
            cpu['load_average'] = [1, cpu_load, 1]

            return cpu, mem

    except TimeoutError as e:
        print(e)
