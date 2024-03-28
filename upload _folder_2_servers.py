import paramiko
import os
import tarfile
from concurrent.futures import ThreadPoolExecutor

def scp_upload(host, username, password, local_folder):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=username, password=password)

        sftp = client.open_sftp()

        # Create a temporary tar archive of the local folder
        tar_filename = 'archive.tar.gz'
        tar_path = os.path.join('/tmp', tar_filename)
        create_tar_archive(local_folder, tar_path)

        # Upload the tar archive to the remote server
        remote_folder = '/tmp'
        sftp.put(tar_path, os.path.join(remote_folder, tar_filename))

        sftp.close()
        client.close()

        return f'Success: {host}'

    except paramiko.AuthenticationException:
        return f'Authentication failed: {host}'

    except paramiko.SSHException as e:
        return f'Error occurred while establishing SSH connection with {host}: {str(e)}'

    except Exception as e:
        return f'Error occurred while connecting to {host}: {str(e)}'


def create_tar_archive(local_folder, tar_path):
    with tarfile.open(tar_path, 'w:gz') as tar:
        for root, _, files in os.walk(local_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, local_folder)
                tar.add(file_path, arcname=arcname)


def main():
    # SSH login credentials
    username = 'your_username'
    password = 'your_password'

    # Local folder to upload
    local_folder = 'C:/path/to/local/folder'

    # Read servers from file
    with open('servers.txt', 'r') as file:
        servers = [line.strip() for line in file]

    # Parallel mode (maximum 5 concurrent transfers)
    concurrency = 5

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = []
        for host in servers:
            future = executor.submit(scp_upload, host, username, password, local_folder)
            futures.append(future)

        for future in futures:
            result = future.result()
            print(result)


if __name__ == '__main__':
    main()
