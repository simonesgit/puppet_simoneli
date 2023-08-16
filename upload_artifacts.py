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

def upload_artifact(file_path, repository, delete_existing=False):
    with open(file_path, "rb") as f:
        relative_path = os.path.relpath(file_path, LOCAL_STORAGE_PATH).replace("\\", "/")
        upload_url = urljoin(NEXUS_URL, f"{UPLOAD_API}/{repository}/{relative_path}")
        
        # Check if the artifact already exists on Nexus
        if delete_existing:
            artifact_url = urljoin(NEXUS_URL, f"{REPOSITORY}/{relative_path}")
            artifact_exists = requests.head(artifact_url, auth=(USERNAME, PASSWORD), verify=SSL_CERT_PATH).status_code == 200
            if artifact_exists:
                delete_url = urljoin(NEXUS_URL, f"{UPLOAD_API}/{repository}/{relative_path}")
                response = requests.delete(delete_url, auth=(USERNAME, PASSWORD), verify=SSL_CERT_PATH)
                response.raise_for_status()
                print(f"Deleted existing artifact at {delete_url}")

        # Upload the artifact
        response = requests.put(
            upload_url,
            data=f,
            auth=(USERNAME, PASSWORD),
            verify=SSL_CERT_PATH,
        )
        response.raise_for_status()
        print(f"Uploaded {file_path} to {repository}")

def upload_all_artifacts(local_storage_path, repository, delete_existing=False):
    for root, _, files in os.walk(local_storage_path):
        for file in files:
            file_path = os.path.join(root, file)
            upload_artifact(file_path, repository, delete_existing)

def main():
    upload_all_artifacts(LOCAL_STORAGE_PATH, REPOSITORY, True)  # Set delete_existing parameter to True if you want to delete existing artifacts

if __name__ == "__main__":
    main()
