import splunklib.client as client
import requests
import os

SPLUNK_HOST = 'your_splunk_host'  # e.g., 'localhost', 'splunk.mydomain.com'
SPLUNK_PORT = 8089                # default management port is 8089
SPLUNK_USERNAME = 'your_username'
SPLUNK_PASSWORD = 'your_password'

service = client.connect(
    host=SPLUNK_HOST,
    port=SPLUNK_PORT,
    username=SPLUNK_USERNAME,
    password=SPLUNK_PASSWORD
)

# Set the search query from the dashboard panel
search_query = '''
| inputlookup filename.csv
| search ...
| table ...
| outputlookup temp_output.csv
'''

# Execute the search query
search_parameters = {
    'exec_mode': 'normal',
    'earliest_time': '0',
    'latest_time': 'now',
}

job = service.jobs.create(search_query, **search_parameters)
while not job.is_done():
    time.sleep(2)  # Wait for the job to complete

# Download the CSV file from the Splunk server
splunk_rest_url = f"https://{SPLUNK_HOST}:{SPLUNK_PORT}/servicesNS/{SPLUNK_USERNAME}/search/lookup-table-files/temp_output.csv"
output_file = "output.csv"

response = requests.get(
    splunk_rest_url,
    auth=(SPLUNK_USERNAME, SPLUNK_PASSWORD),
    verify=False  # Set to True if you have a valid SSL certificate
)

with open(output_file, "wb") as f:
    f.write(response.content)

print(f"Results saved to {output_file}")

# Clean up the temporary CSV file on the Splunk server
os.remove(f"$SPLUNK_HOME/etc/users/{SPLUNK_USERNAME}/search/lookups/temp_output.csv")
