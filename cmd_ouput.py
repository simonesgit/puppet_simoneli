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

# SSH login credentials
username = 'your_username'
password = 'your_password'

# Read hosts from file
with open('Asia-NonProdServers.txt', 'r') as file:
    hosts = file.read().splitlines()

# Open result file for writing
with open('result.txt', 'w') as file:
    for host in hosts:
        output = ssh_login(host, username, password)
        output = output.replace('\n', ' ')  # Replace newlines with spaces
        file.write(f'{host},{output}\n')

print('Results written to result.txt')
