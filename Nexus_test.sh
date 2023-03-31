#!/bin/bash

# Set the Nexus Repository Manager base URL
NEXUS_BASE_URL="http://nexus.example.com"

# Set the name of your hosted raw repository
REPO_NAME="app-repo"

# Set the prefix of your software filename
SOFTWARE_PREFIX="software"

# Set the directory where you want to download the latest software
DOWNLOAD_DIR="/path/to/download/dir"

# Get the list of available versions from Nexus Repository Manager
VERSIONS=$(curl -s "${NEXUS_BASE_URL}/service/rest/v1/search/assets/download?repository=${REPO_NAME}&sort=version&direction=desc" | jq '.items[].version' | sort -r)

# Find the latest version
for VERSION in $VERSIONS; do
  SOFTWARE_URL="${NEXUS_BASE_URL}/repository/${REPO_NAME}/${VERSION}/${SOFTWARE_PREFIX}.zip"
  if curl --head --silent --fail "$SOFTWARE_URL" > /dev/null; then
    echo "Latest version is ${VERSION}"
    echo "Downloading software from ${SOFTWARE_URL}..."
    curl --fail --progress-bar --output "${DOWNLOAD_DIR}/${SOFTWARE_PREFIX}-${VERSION}.zip" "${SOFTWARE_URL}"
    echo "Download complete."
    exit 0
  fi
done

# If no valid version was found, print an error message
echo "No valid version found."
exit 1
