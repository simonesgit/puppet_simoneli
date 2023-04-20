#!/bin/bash

# Variables
REPOSITORY="<your_repository>"
ARTIFACT_GROUP="com/bbc/controlm/linux"
ARTIFACT_PREFIX="scripts/ctmag_support_scripts"
NEXUS_BASE_URL="http://<your_nexus_server>:<port>/service/rest/v1/search"
UNIT_TEST=true

# Function to compare versions
version_compare() {
    printf '%s\n' "$@" | sort -V | tail -n 1
}
# Function to print a message if UNIT_TEST is true
print_if_unit_test() {
    if [ "$UNIT_TEST" = true ]; then
        echo "$1"
    fi
}

if [ "$UNIT_TEST" = true ]; then
    # Dummy ARTIFACTS for testing purposes
    ARTIFACTS='
    {
      "items" : [ {
        "downloadUrl" : "http://your_nexus_server:port/repository/your_repository/com/bbc/controlm/linux/9.0.20/scripts/ctmag_support_scripts-9.0.21.001.zip",
        "path" : "com/bbc/controlm/linux/9.0.22.001/scripts/ctmag_support_scripts-9.0.21.001.zip"
      }, {
        "downloadUrl" : "http://your_nexus_server:port/repository/your_repository/com/bbc/controlm/linux/9.0.21.001/scripts/ctmag_support_scripts-9.0.21.002.zip",
        "path" : "com/bbc/controlm/linux/9.0.21.001/scripts/ctmag_support_scripts-9.0.21.002.zip"
      }, {
        "downloadUrl" : "http://your_nexus_server:port/repository/your_repository/com/bbc/controlm/linux/9.0.21.002/scripts/ctmag_support_scripts-9.0.21.002.zip",
        "path" : "com/bbc/controlm/linux/9.0.21.001/scripts/ctmag_support_scripts-9.0.21.002.zip"
      }, {
        "downloadUrl" : "http://your_nexus_server:port/repository/your_repository/com/bbc/controlm/linux/9.0.22/scripts/ctmag_support_scripts-9.0.22.zip",
        "path" : "com/bbc/controlm/linux/9.0.21.001/scripts/ctmag_support_scripts-9.0.21.002.zip"
      }  ]
    }
    '
else
    # Uncomment this line to use the actual curl request
    ARTIFACTS=$(curl -sSF "${NEXUS_BASE_URL}?repository=${REPOSITORY}&group=/${ARTIFACT_GROUP}/*")
fi

# Filter artifacts based on prefix and extract path versions
PATH_VERSIONS=$(echo "$ARTIFACTS" | grep downloadUrl | grep -oP "${ARTIFACT_GROUP}/[0-9]+(\.[0-9]+)+/${ARTIFACT_PREFIX}" | grep -oP '[0-9]+(\.[0-9]+)+')
print_if_unit_test "$PATH_VERSIONS"

# Find the latest path version
LATEST_PATH_VERSION=""
for VERSION in $PATH_VERSIONS; do
    LATEST_PATH_VERSION=$(version_compare "$LATEST_PATH_VERSION" "$VERSION")
done

print_if_unit_test "Latest path version: ${LATEST_PATH_VERSION}"

# Filter file versions based on the latest path version
FILE_VERSIONS=$(echo "$ARTIFACTS" | grep downloadUrl | grep  "${ARTIFACT_GROUP}/${LATEST_PATH_VERSION}" |grep -oP "/${ARTIFACT_PREFIX}-[0-9]+(\.[0-9]+)+" | grep -oP '[0-9]+(\.[0-9]+)+')
print_if_unit_test "$FILE_VERSIONS"

# Find the latest file version
LATEST_FILE_VERSION=""
for VERSION in $FILE_VERSIONS; do
    LATEST_FILE_VERSION=$(version_compare "$LATEST_FILE_VERSION" "$VERSION")
done

print_if_unit_test "Latest file version: ${LATEST_FILE_VERSION}"

# Find the artifact with the latest path version and latest file version
LATEST_ARTIFACT=$(echo "$ARTIFACTS" | grep -oP "\"downloadUrl\" *: *\"http[^\"]*${ARTIFACT_GROUP}/${LATEST_PATH_VERSION}/${ARTIFACT_PREFIX}-${LATEST_FILE_VERSION}[^\"\n]*\"" | sed -E 's/\"downloadUrl\" *: *\"//;s/\"//')
echo $LATEST_ARTIFACT
