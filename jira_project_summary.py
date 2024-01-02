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
        'filter_name': 'all_epics',
        'filter_id': '123456',
        'filter_fields': ['assignee', 'summary', 'status', 'labels', 'ParentLink']
    },
    {
        'filter_name': 'all_initiatives',
        'filter_id': '234567',
        'filter_fields': ['assignee', 'summary', 'status', 'labels', 'key']
    },
    {
        'filter_name': 'all_stories',
        'filter_id': '345678',
        'filter_fields': ['assignee', 'summary', 'status', 'labels', 'EpicLink']
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
    'assignee': [''],
    # Add more field ID to string format mappings as needed
}

# Set the maximum number of results per page
max_results_per_page = 100

# Helper function to convert field names
def convert_field_names(fields):
    """
    Convert field names in the fields dictionary using field_id_to_name mapping.
    """
    converted_fields = {}
    for field, value in fields.items():
        if field in field_id_to_name:
            converted_fields[field_id_to_name[field]] = value
        else:
            converted_fields[field] = value
    return converted_fields

# Helper function to extract specific field values
def extract_field_values(fields, filter_name):
    """
    Extract specific values from dictionary-format fields and construct a string representation.
    """
    extracted_fields = {}
    for field, extraction_keys in field_dict_to_string.items():
        if field in fields and fields[field] is not None and isinstance(fields[field], dict):
            extracted_values = [str(fields[field].get(key, '')) for key in extraction_keys]
            extracted_fields[field] = ' - '.join(extracted_values)
        else:
            extracted_fields[field] = fields.get(field, '')

    # Apply summary splitting logic for 'all_initiatives' filter
    if filter_name == 'all_initiatives':
        summary = fields.get('summary', '')
        if ' - ' in summary:
            project, initiative = summary.split(' - ', 1)
        else:
            project = 'Others'
            initiative = ''
        extracted_fields['Project'] = project
        extracted_fields['Initiative'] = initiative

    return extracted_fields

# Helper function to extract labels and convert them into a string format
def extract_labels(labels):
    """
    Extract and convert labels field to a string format separated by '|' with spaces.
    """
    if labels is not None and isinstance(labels, list):
        return ' | '.join(labels)
    return ''

# Iterate over the filters list
for filter_data in filters:
    filter_name = filter_data['filter_name']
    filter_id = filter_data['filter_id']
    filter_fields = filter_data['filter_fields']

    # Send an HTTP GET request to retrieve the Jira filter results
    response = requests.get(filter_url.format(filter_id), auth=(username, password), verify=ca_file_path)

    # Check if the response is successful
    if response.status_code == 200:
        # Extract the JSON data from the response
        data = response.json()

        # Write the full content of the data to a file for debugging
        with open(f'{filter_name}_data.json', 'w') as file:
            json.dump(data, file, indent=4)

        # Extract the individual issues from the JSON data
        issues = data.get('issues', [])

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
            extracted_fields = extract_field_values(converted_fields, filter_name)

            # Extract and convert labels field toa string separated by | with spaces
            extracted_fields['labels'] = extract_labels(fields.get('labels'))

            # Remove the 'summary' field from the extracted fields for non 'all_initiatives' filters
            if filter_name != 'all_initiatives':
                extracted_fields.pop('summary', None)

            # Add the fields that are not mentioned in field_dict_to_string
            for field, value in converted_fields.items():
                if field not in extracted_fields:
                    extracted_fields[field] = value

            # Move 'key' field to the beginning of the dictionary
            extracted_fields = {'key': key, **extracted_fields}

            # Append the fields dictionary to the issue_details list
            issue_details.append(extracted_fields)

        # Create a DataFrame from the issue_details list
        df = pd.DataFrame(issue_details)

        # Reorder the columns
        column_order = ['key'] + filter_fields
        df = df[column_order]

        # Save the DataFrame to a CSV file
        df.to_csv(f'{filter_name}_issues.csv', index=False)

        print(f"CSV export for {filter_name} completed successfully. File: {csv_file_name}")
        print("Head of the DataFrame:")
        print(df.head())
    else:
        print(f"Error retrieving Jira filter results for {filter_name}. Status code: {response.status_code}. Response content: {response.content}")



# Read the CSV files into DataFrames
dfs = {}
for filter_data in filters:
    filter_name = filter_data['filter_name']
    df = pd.read_csv(f'{filter_name}_issues.csv')
    dfs[filter_name] = df

# Merge all_initiatives and all_epics by associating all_initiatives.key and all_epics.ParentLink
if 'all_initiatives' in dfs and 'all_epics' in dfs:
    all_initiatives_df = dfs['all_initiatives']
    all_epics_df = dfs['all_epics']
    merged_df = pd.merge(all_initiatives_df, all_epics_df, left_on='key', right_on='ParentLink', suffixes=('_initiative', '_epic'))
else:
    raise ValueError("Missing all_initiatives or all_epics DataFrame")

# Calculate the number of 'In Progress' stories for each epic
if 'all_stories' in dfs:
    all_stories_df = dfs['all_stories']
    in_progress_stories = all_stories_df[all_stories_df['status'] == 'In Progress']
    wip_stories = in_progress_stories.groupby('EpicLink').size().reset_index(name='WIP_stories')
    merged_df = pd.merge(merged_df, wip_stories, left_on='key_epic', right_on='EpicLink', how='left')
else:
    raise ValueError("Missing all_stories DataFrame")

# Add prefix to the column names of all_initiatives and all_epics
merged_df = merged_df.add_prefix('initiative_')
merged_df.rename(columns={'initiative_key_initiative': 'key_initiative'}, inplace=True)
merged_df.rename(columns={'initiative_key_epic': 'key_epic'}, inplace=True)

# Export the final result as 'project_overview_raw.csv'
merged_df.to_csv('project_overview_raw.csv', index=False)
