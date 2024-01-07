import csv
import requests
import json
from tqdm import tqdm

# Global variables
jira_api_endpoint = 'https://your-jira-instance/rest/api/2'

# Read credentials from a file
with open('credentials.txt', 'r') as file:
    credentials = json.load(file)

# SSL verification using a CA file
ca_file_path = '/path/to/your/ca/file.pem'


def get_latest_comment(issue_key):
    # API endpoint
    api_url_template = f"{jira_api_endpoint}/issue/{{}}/comment"

    # Construct the API endpoint for the specific issue
    api_url = api_url_template.format(issue_key)

    # Make the API request
    response = requests.get(api_url, headers={'Content-Type': 'application/json'},
                            auth=(credentials['username'], credentials['password']), verify=ca_file_path)

    if response.status_code == 200:
        # Parse the response
        comments = response.json()['comments']
        latest_comment = comments[-1]['body'] if comments else "No comments found."
        formatted_comment = format_comment(latest_comment)
        return formatted_comment
    else:
        return f"Error: {response.status_code} - {response.text}"


def format_comment(comment):
    lines = comment.split('\n')
    formatted_lines = []

    for line in lines:
        if line.startswith(' * '):
            line = '  - ' + line[3:]
        formatted_lines.append(line)

    return '\n'.join(formatted_lines)


def get_latest_comments(csv_file_name, issue_key_column):
    updated_rows = []

    with open(csv_file_name, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        fieldnames = csv_reader.fieldnames + ['last_comment']
        total_rows = sum(1 for _ in csv_reader)  # Count total rows in the CSV file

    with open(csv_file_name, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in tqdm(csv_reader, total=total_rows, unit='row'):
            issue_key = row[issue_key_column]
            summary = row['E_summary']
            last_comment = get_latest_comment(issue_key)
            row['last_comment'] = last_comment
            updated_rows.append(row)

    with open(csv_file_name, 'w', newline='', encoding='utf-8') as file:
        csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(updated_rows)


if __name__ == '__main__':
    # CSV file name and issue key column
    csv_file_name = 'issues.csv'
    issue_key_column = 'issue_key'

    # Call the function to update the CSV file
    get_latest_comments(csv_file_name, issue_key_column)
    print(f"CSV file '{csv_file_name}' has been updated with the latest comments.")
