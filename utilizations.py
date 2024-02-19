import paramiko


def get_stat(host, username, password, port=22):
    data = []
    cpu = {}
    load = []
    mem = {}
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=username, password=password, port=port)
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
    except TimeoutError as e:
        print(e)
