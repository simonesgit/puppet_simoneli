import requests
import time
import os

SPLUNK_HOST = 'your_splunk_host'  # e.g., 'localhost', 'splunk.mydomain.com'
SPLUNK_PORT = 8089                # default management port is 8089
SPLUNK_USERNAME = 'your_username'
SPLUNK_PASSWORD = 'your_password'

# Set the search query from the dashboard panel
search_query = '''
| inputlookup filename.csv
| search ...
| table ...
'''

# Set the URL for the Splunk REST API
url = f"https://{SPLUNK_HOST}:{SPLUNK_PORT}/services/search/jobs/export"

# Set up the request parameters
request_params = {
    "output_mode": "csv",
    "search": f"search {search_query}",
    "earliest_time": "0",
    "latest_time": "now",
}

# Send the request to the Splunk REST API
response = requests.post(
    url,
    auth=(SPLUNK_USERNAME, SPLUNK_PASSWORD),
    data=request_params,
    verify=False  # Set to True if you have a valid SSL certificate
)

# Save the results to a file
output_file = 'output.csv'
with open(output_file, 'wb') as f:
    f.write(response.content)

print(f"Results saved to {output_file}")
