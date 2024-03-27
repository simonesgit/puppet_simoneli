import paramiko
import os
import tarfile
from stat import S_ISDIR
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

        # Extract the tar archive on the remote server
        extract_tar_archive(sftp, os.path.join(remote_folder, tar_filename), remote_folder)

        # Set global readable permissions on the remote folder and its sub-elements
        set_global_readable(sftp, os.path.join(remote_folder, os.path.basename(local_folder.rstrip('/'))))

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
        tar.add(local_folder, arcname=os.path.basename(local_folder))


def extract_tar_archive(sftp, tar_path, remote_folder):
    with tarfile.open(tar_path, 'r:gz') as tar:
        tar.extractall(remote_folder)


def remote_folder_exists(sftp, remote_folder):
    try:
        return S_ISDIR(sftp.stat(remote_folder).st_mode)
    except FileNotFoundError:
        return False


def set_global_readable(sftp, remote_folder):
    sftp.chmod(remote_folder, 0o755)  # Set folder permissions to 755
    for item in sftp.listdir_attr(remote_folder):
        path = remote_folder + '/' + item.filename
        if S_ISDIR(item.st_mode):
            set_global_readable(sftp, path)  # Recursively set permissions for sub-folders
        else:
            sftp.chmod(path, 0o644)  # Set file permissions to 644


def main():
    # SSH login credentials
    username = 'your_username'
    password = 'your_password'

    # Local folder to upload
    local_folder = '/path/to/local/folder'

    # Read servers from file
    with open('server.txt', 'r') as file:
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
