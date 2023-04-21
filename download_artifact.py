import os
import requests
from urllib.parse import urljoin

# Replace with your Nexus URL, credentials, repository name, and local storage path
NEXUS_URL = "https://nexus.example.com"
USERNAME = "your_username"
PASSWORD = "your_password"
REPOSITORY = "your_repository"
LOCAL_STORAGE_PATH = "/path/to/local/storage"

# Nexus REST API endpoint
SEARCH_API = "/service/rest/v1/search"

def get_all_artifacts(repository):
    artifacts = []
    url = urljoin(NEXUS_URL, SEARCH_API)
    params = {
        "repository": repository,
    }

    while url:
        response = requests.get(url, params=params, auth=(USERNAME, PASSWORD))
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

    response = requests.get(download_url, auth=(USERNAME, PASSWORD), stream=True)
    response.raise_for_status()

    with open(local_file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"Downloaded {download_url} to {local_file_path}")

def main():
    artifacts = get_all_artifacts(REPOSITORY)

    for artifact in artifacts:
        download_artifact(artifact, LOCAL_STORAGE_PATH)

if __name__ == "__main__":
    main()
