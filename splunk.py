import splunklib.client as client
import splunklib.results as results

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



search_query = 'your_search_query'  # e.g., 'search index=_internal | head 10'
search_parameters = {'exec_mode': 'normal'}

job = service.jobs.create(search_query, **search_parameters)
while not job.is_done():
    time.sleep(2)  # Wait for the job to complete

results_reader = results.ResultsReader(job.results())
for result in results_reader:
    print(result)
##
report_id = 'your_report_id'  # e.g., 'my_saved_search'
report = service.saved_searches[report_id]

search_query = report["search"]
search_parameters = {'exec_mode': 'normal'}

job = service.jobs.create(search_query, **search_parameters)
while not job.is_done():
    time.sleep(2)  # Wait for the job to complete

results_reader = results.ResultsReader(job.results())
for result in results_reader:
    print(result)
