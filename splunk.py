import splunklib.client as client
import pandas as pd
import io
import time

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

# Get the results in CSV format
csv_data = job.results(output_mode='csv').read()

# Read the results as a pandas DataFrame
data_frame = pd.read_csv(io.StringIO(csv_data.decode('utf-8')))

print(data_frame)
