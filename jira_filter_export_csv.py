import requests
import pandas as pd
import json

# Define the Jira filter URL
filter_url = "https://your-jira-instance/rest/api/2/search?jql=filter={}"

# Define the path to the CA file
ca_file_path = "/path/to/your/ca_file.pem"

# Read Jira credentials from JSON file
with open('jira_credentials.json', 'r') as file:
    credentials = json.load(file)

username = credentials["username"]
password = credentials["password"]

# Define the list of filters
filters = [
    {
        'filter_name': 'filter1',
        'filter_id': '234567',
        'filter_fields': ['assignee', 'summary', 'status', 'labels']
    },
    {
        'filter_name': 'filter2',
        'filter_id': '987654',
        'filter_fields': ['assignee', 'summary', 'priority']
    }
    # Add more filters as needed
]

# Customized field ID to name mapping
field_id_to_name = {
    "customfield_1": "Custom Field 1",
    "customfield_2": "Custom Field 2",
    # Add more field ID to name mappings as needed
}

# Customized field ID to string format mapping
field_dict_to_string = {
    'assignee': ['displayName', 'emailAddress'],
    # Add more fields and their extraction keys as needed
}

# Set the maximum number of results per page
max_results = 200

def convert_field_names(fields):
    """
    Converts the names of customized fields in the given fields dictionary.
    """
    converted_fields = {}
    for field, value in fields.items():
        if field in field_id_to_name:
            converted_fields[field_id_to_name[field]] = value
        else:
            converted_fields[field] = value
    return converted_fields

def extract_field_values(fields):
    """
    Extracts specific values from dictionary-format fields and constructs a string representation.
    """
    extracted_fields = {}
    for field, extraction_keys in field_dict_to_string.items():
        if field in fields and fields[field] is not None and isinstance(fields[field], dict):
            extracted_values = [str(fields[field].get(key, '')) for key in extraction_keys]
            extracted_fields[field] = ' - '.join(extracted_values)
        else:
            extracted_fields[field] = fields.get(field, '')
    return extracted_fields

def extract_labels(labels):
    """
    Extracts labels and converts them into a string format separated by | with spaces.
    """
    if labels is not None and isinstance(labels, list):
        return ' | '.join(labels)
    return ''

for filter_data in filters:
    filter_name = filter_data['filter_name']
    filter_id = filter_data['filter_id']
    filter_fields = filter_data['filter_fields']

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
            # Extract the key and fields from the issue
            key = issue['key']
            fields = issue['fields']

            # Convert the field names in the fields dictionary
            converted_fields = convert_field_names(fields)

            # Extract specific values from dictionary-format fields and construct a string representation
            extracted_fields = extract_field_values(converted_fields)

            # Extract and convert labels field to a string separated by | with spaces
            extracted_fields['labels'] = extract_labels(fields.get('labels'))

            # Add the fields that are not mentioned in field_dict_to_string
            for field, value in converted_fields.items():
                if field not in extracted_fields:
                    extracted_fields[field] = value

            # Move 'key' field to the beginning of the dictionary
            extracted_fields = {'key': key, **extracted_fields}

            # Append the fields dictionary to the issue_details list
            issue_details.append(extracted_fields)

        # Create a pandas DataFrame from the issue_details list
        df = pd.DataFrame(issue_details)

        # Filter columns based on filter_fields if it is not empty
        if filter_fields:
            filter_columns = ['key'] + [col for col in df.columns if col in filter_fields]
            df = dfcontd...

        # Write the DataFrame to a CSV file
        csv_file_name = f"{filter_name}_result.csv"
        df.to_csv(csv_file_name, index=False)

        print(f"CSV export for {filter_name} completed successfully. File: {csv_file_name}")
        print("Head of the DataFrame:")
        print(df.head())
    else:
        print(f"Error retrieving Jira filter results for {filter_name}. Status code: {response.status_code}. Response content: {response.content}")
