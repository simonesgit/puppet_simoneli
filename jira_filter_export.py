import requests
import pandas as pd
from bs4 import BeautifulSoup


# Jira filter URL
filter_url = "https://your-jira-instance/rest/api/2/search?jql=filter={}"
filter_id = '234567'

# Jira credentials
username = "your_username"
password = "your_password"

# Path to the CA file
ca_file_path = "/path/to/your/ca_file.pem"

# Send HTTP GET request to retrieve Jira filter results
response = requests.get(filter_url.format(filter_id), auth=(username, password), verify=ca_file_path)

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

    # Convert DataFrame to HTML table
    html_table = df.to_html(index=False)

    # Create BeautifulSoup object
    soup = BeautifulSoup(html_table, 'html.parser')

    # Create a prettified HTML string
    html_string = soup.prettify()

    # Write the HTML string to a file
    with open('jira_filter_results.html', 'w', encoding='utf-8') as file:
        file.write(html_string)

    # Print a sample of the DataFrame
    print(df.head())

else:
    print("Error occurred while retrieving Jira filter results. Status code:", response.status_code)
    print("Response content:", response.content.decode())
