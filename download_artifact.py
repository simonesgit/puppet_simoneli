import os
import requests
from urllib.parse import urljoin

# Replace with your Nexus URL, credentials, repository name, and group filter
NEXUS_URL = "https://nexus.example.com"
USERNAME = "your_username"
PASSWORD = "your_password"
REPOSITORY = "your_repository"
GROUP_FILTER = "your_group"

# Nexus REST API endpoint
SEARCH_API = "/service/rest/v1/search"

# Local storage path
LOCAL_STORAGE_PATH = "./download"

# SSL certificate path
SSL_CERT_PATH = "./root_ca.pem"

def get_all_artifacts(repository, group_filter):
    artifacts = []
    url = urljoin(NEXUS_URL, SEARCH_API)
    params = {
        "repository": repository,
        "group": f"{group_filter}*",
    }

    while url:
        response = requests.get(url, params=params, auth=(USERNAME, PASSWORD), verify=SSL_CERT_PATH)
        response.raise_for_status()
        data = response.json()

        artifacts.extend(data["items"])
        url = data["continuationToken"] if data["continuationToken"] else None
        params["continuationToken"] = url

    return artifacts

def download_artifact(artifact, local_storage_path):
    download_url = artifact["assets"][0]["downloadUrl"]
    path = artifact["assets"][0]["path"]
    local_file_path = os.path.join(local_storage_path, path)

    os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

    response = requests.get(download_url, auth=(USERNAME, PASSWORD), verify=SSL_CERT_PATH, stream=True)
    response.raise_for_status()

    with open(local_file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"Downloaded {download_url} to {local_file_path}")

def main():
    artifacts = get_all_artifacts(REPOSITORY, GROUP_FILTER)

    for artifact in artifacts:
        download_artifact(artifact, LOCAL_STORAGE_PATH)

if __name__ == "__main__":
    main()
