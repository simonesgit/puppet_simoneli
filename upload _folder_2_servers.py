import paramiko
import os
from stat import S_ISDIR
from concurrent.futures import ThreadPoolExecutor


def scp_upload(host, username, password, local_folder):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=username, password=password)

        sftp = client.open_sftp()

        # Create the remote directory if it does not exist
        remote_folder = '/tmp/' + os.path.basename(local_folder.rstrip('/'))
        if not remote_folder_exists(sftp, remote_folder):
            sftp.mkdir(remote_folder)

        # Upload files recursively
        for root, dirs, files in os.walk(local_folder):
            remote_dir = remote_folder + root[len(local_folder):]
            for d in dirs:
                remote_path = os.path.join(remote_dir, d)
                if not remote_folder_exists(sftp, remote_path):
                    sftp.mkdir(remote_path)
            for f in files:
                local_path = os.path.join(root, f)
                remote_path = os.path.join(remote_dir, f)
                sftp.put(local_path, remote_path)

        # Set global readable permissions on the remote folder and its sub-elements
        set_global_readable(sftp, remote_folder)

        sftp.close()
        client.close()

        return f'Success: {host}'

    except paramiko.AuthenticationException:
        return f'Authentication failed: {host}'

    except paramiko.SSHException as e:
        return f'Error occurred while establishing SSH connection with {host}: {str(e)}'

    except Exception as e:
        return f'Error occurred while connecting to {host}: {str(e)}'


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
