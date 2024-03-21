import paramiko
import time
import csv
from concurrent.futures import ThreadPoolExecutor


def ssh_login(host, username, password, cmd_profile):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=username, password=password)

        shell = client.invoke_shell()

        with open(cmd_profile, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                if not row[0].startswith('#'):  # Ignore lines beginning with '#'
                    command, wait_time = row
                    shell.send(command + '\n')
                    time.sleep(int(wait_time))

                    while shell.recv_ready():
                        output = shell.recv(1024).decode()

        return output

    except paramiko.AuthenticationException:
        print(f'Authentication failed for {host}')
        return f'{host},Authentication failed'

    except paramiko.SSHException as e:
        print(f'Error occurred while establishing SSH connection with {host}: {str(e)}')
        return f'{host},Error occurred while establishing SSH connection with {host}: {str(e)}'

    except Exception as e:
        print(f'Error occurred while connecting to {host}: {str(e)}')
        return f'{host},Error occurred while connecting to {host}: {str(e)}'


def main():
    # SSH login credentials
    username = '45348'
    password = 'BHAP9'

    # Read servers from file (renamed from inputfile to input_servers)
    input_servers = 'test.txt'
    servers = []
    with open(input_servers, 'r') as file:
        for line in file:
            line = line.strip()
            if not line.startswith('#'):
                servers.append(line)

    # cmd_profile file
    cmd_profile = 'cmd_profile.txt'

    # Open result file for writing
    outputfile = input_servers.replace('.txt', '') + '_result.txt'

    # Number of concurrent sessions
    concurrency = 5

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = []
        for host in servers:
            future = executor.submit(ssh_login, host, username, password, cmd_profile)
            futures.append(future)

        with open(outputfile, 'w') as file:
            for host, future in zip(servers, futures):
                output = future.result()
                file.write(f'{host},{output}\n')

    print('Results written to', outputfile)


if __name__ == '__main__':
    main()
