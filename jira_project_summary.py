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
        'filter_name': 'all_initiatives',
        'filter_id': '234567',
        'filter_fields': ['assignee', 'summary', 'status', 'labels']
    },
    {
        'filter_name': 'all_epics',
        'filter_id': '987654',
        'filter_fields': ['assignee', 'summary', 'priority', 'ParentLink']
    },
    {
        'filter_name': 'all_stories',
        'filter_id': '876543',
        'filter_fields': ['assignee', 'summary', 'priority', 'EpicLink', 'status']
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

def process_initiatives(df):
    """
    Process the 'all_initiatives' DataFrame by adding 'Project' and 'Initiative' columns and removing 'summary' column.
    """
    df['Project'] = df['summary'].apply(lambda x: x.split(' - ')[0] if ' - ' in x else 'Others')
    df['Initiative'] = df['summary'].apply(lambda x: x.split(' - ')[1] if ' - ' in x else '')
    df.drop('summary', axis=1, inplace=True)
    return df

def merge_dataframes(initiatives_df, epics_df):
    """
    Merge the 'all_initiatives' and 'all_epics' DataFrames based on 'ParentLink' and add prefix to shared column names.
    """
    merged_df = pd.merge(initiatives_df, epics_df, left_on='key', right_on='ParentLink', how='left', suffixes=('_initiative', '_epic'))
    return merged_df

def calculate_wip_stories(df):
    """
    Calculate the number of stories with status 'In Progress' for each epic and add it as the 'WIP_stories' column.
    """
    wip_stories = df[df['status'] == 'In Progress'].groupby('EpicLink')['EpicLink'].count()
    df['WIP_stories'] = df['EpicLink'].map(wip_stories).fillna(0)
    return df

def retrieve_jira_filter_results(filter_name, filter_id):
    filter_url = f"https://your-jira-instance/rest/api/2/search?jql=filter={filter_id}"

    # Send HTTP GET request to retrieve Jira filter results
    response = requests.get(filter_url, auth=(username, password), verify=ca_file_path, params={'maxResults': max_results})

    if response.status_code == 200:
        # Filter results retrieved successfully
        print(f"Jira filter results for {filter_name} retrieved successfully.")
        response_json = response.json()
        issues = response_json.get("issues", [])
    
        # Extract and process the relevant fields from each issue
        data = []
        for issue in issues:
            fields = issue.get("fields", {})
            converted_fields = convert_field_names(fields)
            extracted_fields = extract_field_values(converted_fields)
            extracted_fields["labels"] = extract_labels(fields.get("labels"))
            data.append(extracted_fields)
    
        # Create a DataFrame from the extracted data
        df = pd.DataFrame(data)
        
        # Process the DataFrame based on the filter name
        if filter_name == "all_initiatives":
            df = process_initiatives(df)
        elif filter_name == "all_epics":
            pass  # Additional processing for the 'all_epics' filter can be added here
        elif filter_name == "all_stories":
            df = calculate_wip_stories(df)
        
        # Print the resulting DataFrame
        print(f"DataFrame for {filter_name}:")
        print(df)
        print()
    else:
        # Error retrieving Jira filter results
        print(f"Error retrieving Jira filter results for {filter_name}.")
        print(f"Status code: {response.status_code}")
        print("Response content:")
        print(response.content)

# Iterate over the list of filters
for filter_info in filters:
    filter_name = filter_info['filter_name']
    filter_id = filter_info['filter_id']
    filter_fields = filter_info['filter_fields']
    
    # Call retrieve_jira_filter_results() function
    retrieve_jira_filter_results(filter_name, filter_id, filter_fields)
    
# Merge 'all_initiatives' and 'all_epics' DataFrames
merged_df = merge_dataframes(initiatives_df, epics_df)

# Calculate WIP stories for each epic
final_df = calculate_wip_stories(merged_df)

# Export final result to CSV file
final_df.to_csv('project_overview_raw.csv', index=False)
