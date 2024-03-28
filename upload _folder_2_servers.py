import paramiko
import os
import tarfile
import concurrent.futures

def scp_upload(hosts, username, password, local_folder):
    try:
        # Create a temporary tar archive of the local folder
        tar_filename = 'archive.tar.gz'
        tar_path = os.path.join('/tmp', tar_filename)
        create_tar_archive(local_folder, tar_path)

        # Upload the tar archive to the remote servers in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = []
            for host in hosts:
                results.append(executor.submit(upload_file, host, username, password, tar_path, '/tmp'))
            
            # Process the results
            for idx, result in enumerate(concurrent.futures.as_completed(results)):
                host = hosts[idx]
                if result.exception() is None:
                    print(f'Success: {host}')
                else:
                    print(f'Error occurred while connecting to {host}: {str(result.exception())}')

    except Exception as e:
        print(f'Error occurred: {str(e)}')


def create_tar_archive(local_folder, tar_path):
    with tarfile.open(tar_path, 'w:gz') as tar:
        tar.add(local_folder, arcname=os.path.basename(local_folder))


def upload_file(host, username, password, local_path, remote_path):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=username, password=password)

    sftp = client.open_sftp()
    sftp.put(local_path, os.path.join(remote_path, os.path.basename(local_path)))
    sftp.close()
    client.close()

def main():
    # Example usage
    hosts = ['example1.com', 'example2.com', 'example3.com', 'example4.com', 'example5.com']
    username = 'your_username'
    password = 'your_password'
    local_folder_path = 'path_to_local_folder'

    # Ensure the local_folder_path ends with '/'
    if not local_folder_path.endswith('/'):
        local_folder_path += '/'

    scp_upload(hosts, username, password, local_folder_path)

if __name__ == "__main__":
    main()
