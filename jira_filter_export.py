import requests
import pandas as pd

# Jira filter URL
filter_url = "https://your-jira-instance/rest/api/2/search?jql=filter=<filter_id>"

# Jira credentials
username = "your_username"
password = "your_password"

# Path to the CA file
ca_file_path = "/path/to/your/ca_file.pem"

# Send HTTP GET request to retrieve Jira filter results
response = requests.get(filter_url, auth=(username, password), verify=ca_file_path)

if response.status_code == 200:
    # Extract the JSON data from the response
    data = response.json()

    # Extract the individual issues from the JSON data
    issues = data['issues']

    # Create an empty list to store the extracted issue details
    issue_details = []

    # Extract all fields from each issue
    for issue in issues:
        # Extract the fields dictionary
        fields = issue['fields']

        # Append the fields dictionary to the issue_details list
        issue_details.append(fields)

    # Create a pandas DataFrame from the issue_details list
    df = pd.DataFrame(issue_details)

    # Print a sample of the DataFrame
    print(df.head())

    # Export the DataFrame to a CSV file
    df.to_csv('jira_filter_results.csv', index=False)

else:
    print("Error occurred while retrieving Jira filter results. Status code:", response.status_code)
    print("Response content:", response.content.decode())
