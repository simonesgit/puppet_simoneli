#!/bin/bash

# Variables
REPOSITORY="<your_repository>"
ARTIFACT_GROUP="com/bbc/controlm/linux/scripts"
ARTIFACT_PREFIX="ctmag_support_scripts"
NEXUS_BASE_URL="http://<your_nexus_server>:<port>/service/rest/v1/search"
UNIT_TEST=true

# Function to compare versions
version_compare() {
    printf '%s\n' "$@" | sort -V | tail -n 1
}

if [ "$UNIT_TEST" = true ]; then
    # Dummy ARTIFACTS for testing purposes
    ARTIFACTS='
    {
      "items" : [ {
        "downloadUrl" : "http://your_nexus_server:port/repository/your_repository/com/bbc/controlm/linux/scripts/9.0.20/ctmag_support_scripts-9.0.21.001.zip",
        "path" : "com/bbc/controlm/linux/scripts/9.0.22.001/ctmag_support_scripts-9.0.21.001.zip"
      }, {
        "downloadUrl" : "http://your_nexus_server:port/repository/your_repository/com/bbc/controlm/linux/scripts/9.0.21/ctmag_support_scripts-9.0.21.002.zip",
        "path" : "com/bbc/controlm/linux/scripts/9.0.21.001/ctmag_support_scripts-9.0.21.002.zip"
      }, {
        "downloadUrl" : "http://your_nexus_server:port/repository/your_repository/com/bbc/controlm/linux/scripts/9.0.21.001/ctmag_support_scripts-9.0.21.001.zip",
        "path" : "com/bbc/controlm/linux/scripts/9.0.21.001/ctmag_support_scripts-9.0.21.002.zip"
      }, {
        "downloadUrl" : "http://your_nexus_server:port/repository/your_repository/com/bbc/controlm/linux/scripts/9.0.21.001/ctmag_support_scripts-9.0.21.002.zip",
        "path" : "com/bbc/controlm/linux/scripts/9.0.21.001/ctmag_support_scripts-9.0.21.002.zip"
      } ]
    }
    '
else
    # Uncomment this line to use the actual curl request
    ARTIFACTS=$(curl -sSF "${NEXUS_BASE_URL}?repository=${REPOSITORY}&group=/${ARTIFACT_GROUP}/*")
fi

# Filter artifacts based on prefix and extract path versions
PATH_VERSIONS=$(echo "$ARTIFACTS" | grep downloadUrl | grep -oP "${ARTIFACT_GROUP}/[0-9]+(\.[0-9]+)+/${ARTIFACT_PREFIX}" | grep -oP '[0-9]+(\.[0-9]+)+')

if [ "$UNIT_TEST" = true ]; then
    echo $PATH_VERSIONS
fi

# Find the latest path version
LATEST_PATH_VERSION=""
for VERSION in $PATH_VERSIONS; do
    LATEST_PATH_VERSION=$(version_compare "$LATEST_PATH_VERSION" "$VERSION")
done

if [ "$UNIT_TEST" = true ]; then
    echo "Latest path version: ${LATEST_PATH_VERSION}"
fi

# Filter file versions based on the latest path version
FILE_VERSIONS=$(echo "$ARTIFACTS" | grep downloadUrl | grep  "${ARTIFACT_GROUP}/${LATEST_PATH_VERSION}" |grep -o
