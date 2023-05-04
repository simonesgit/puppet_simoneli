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
create_job_url = f"https://{SPLUNK_HOST}:{SPLUNK_PORT}/services/search/jobs"

# Set up the request parameters
create_job_params = {
    "search": f"search {search_query}",
    "exec_mode": "normal",
    "earliest_time": "0",
    "latest_time": "now",
}

# Send the request to create a search job
response = requests.post(
    create_job_url,
    auth=(SPLUNK_USERNAME, SPLUNK_PASSWORD),
    data=create_job_params,
    verify=False  # Set to True if you have a valid SSL certificate
)

# Get the search job SID
response_xml = response.text
sid_start = response_xml.find("<sid>") + 5
sid_end = response_xml.find("</sid>")
sid = response_xml[sid_start:sid_end]

# Poll the search job until it's done
job_status_url = f"{create_job_url}/{sid}"
job_is_done = False

while not job_is_done:
    response = requests.get(
        job_status_url,
        auth=(SPLUNK_USERNAME, SPLUNK_PASSWORD),
        verify=False
    )
    response_xml = response.text
    is_done_start = response_xml.find("<isDone>") + 8
    is_done_end = response_xml.find("</isDone>")
    is_done_value = response_xml[is_done_start:is_done_end]
    job_is_done = is_done_value == "1"
    time.sleep(2)

# Fetch the search results as CSV
results_url = f"{job_status_url}/results"
results_params = {
    "output_mode": "csv",
}

response = requests.get(
    results_url,
    auth=(SPLUNK_USERNAME, SPLUNK_PASSWORD),
    params=results_params,
    verify=False
)

# Save the results to a file
output_file = 'output.csv'
with open(output_file, 'wb') as f:
    f.write(response.content)

print(f"Results saved to {output_file}")
