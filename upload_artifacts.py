import os
import requests
from urllib.parse import urljoin

# Replace with your Nexus URL, credentials, and repository name
NEXUS_URL = "https://nexus.example.com"
USERNAME = "your_username"
PASSWORD = "your_password"
REPOSITORY = "your_repository"

# Local storage path
LOCAL_STORAGE_PATH = "./download"

# SSL certificate path
SSL_CERT_PATH = "./root_ca.pem"

# Nexus REST API endpoint
UPLOAD_API = "/repository"

def upload_artifact(file_path, repository):
    with open(file_path, "rb") as f:
        relative_path = os.path.relpath(file_path, LOCAL_STORAGE_PATH).replace("\\", "/")
        upload_url = urljoin(NEXUS_URL, f"{UPLOAD_API}/{repository}/{relative_path}")
        response = requests.put(
            upload_url,
            data=f,
            auth=(USERNAME, PASSWORD),
            verify=SSL_CERT_PATH,
        )
        response.raise_for_status()
        print(f"Uploaded {file_path} to {repository}")

def upload_all_artifacts(local_storage_path, repository):
    for root, _, files in os.walk(local_storage_path):
        for file in files:
            file_path = os.path.join(root, file)
            upload_artifact(file_path, repository)

def main():
    upload_all_artifacts(LOCAL_STORAGE_PATH, REPOSITORY)

if __name__ == "__main__":
    main()
