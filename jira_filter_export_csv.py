import requests
import pandas as pd

# Jira filter URL
filter_url = "https://your-jira-instance/rest/api/2/search?jql=filter={}"
filter_id = '234567'

# Jira credentials
username = "your_username"
password = "your_password"

# Path to the CA file
ca_file_path = "/path/to/your/ca_file.pem"

# Set the maximum number of results per page
max_results = 200

# Send HTTP GET request to retrieve Jira filter results
response = requests.get(filter_url.format(filter_id), auth=(username, password), verify=ca_file_path, params={'maxResults': max_results})

if response.status_code == 200:
    # Extract the JSON data from the response
    data = response.json()

    # Write the full content of data to a file for debugging
    with open('jira_filter_json.txt', 'w') as file:
        file.write(str(data))

    # Extract the individual issues from the JSON data
    issues = data['issues']

    # Create an empty list to store the extracted issue details
    issue_details = []

    # Extract all fields from each issue
    for issue in issues:
        # Extract the fields dictionary
        fields = issue['fields']

        # Remove fields with 0 contents
        fields = {key: value for key, value in fields.items() if value}

        # Append the fields dictionary to the issue_details list
        issue_details.append(fields)

    # Create a pandas DataFrame from the issue_details list
    df = pd.DataFrame(issue_details)

    # Write the DataFrame to a CSV file
    df.to_csv('jira_filter_results.csv', index=False)

    # Print a sample of the DataFrame
    print(df.head())

else:
    print("Error occurred while retrieving Jira filter results. Status code:", response.status_code)
    print("Response content:", response.content.decode())
