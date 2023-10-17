import paramiko

def ssh_login(host, username, password):
    try:
        # Create SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the host
        client.connect(hostname=host, username=username, password=password)

        # Execute the command
        stdin, stdout, stderr = client.exec_command('which java')

        # Get the output of the command
        output = stdout.read().decode().strip()

        # Close the SSH connection
        client.close()

        return output
    except paramiko.AuthenticationException:
        print(f'Authentication failed for {host}')
    except paramiko.SSHException as e:
        print(f'Unable to establish SSH connection with {host}: {str(e)}')
    except Exception as e:
        print(f'Error occurred while connecting to {host}: {str(e)}')

# List of hosts
hosts = ['host1', 'host2', 'host3']
username = 'your_username'
password = 'your_password'

for host in hosts:
    output = ssh_login(host, username, password)
    print(f'[{host}] Output of `which java`: {output}')
