import csv
import json
import requests
from tabulate import tabulate
import textwrap
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import webbrowser
import os

# Define the API URL pattern
API_URL_PATTERN = "https://cp-m.ccc/apl/v3/read?changeRequest={}&withChangeTasks=false&withPamTasks=false"

# Read change order numbers from CSV file
with open('change_orders.csv', 'r', encoding='utf-8') as file:
    change_order_numbers = [line.strip() for line in file]

# Initialize lists to store data
comprehensive_data = []
brief_summary_data = []
raw_responses = []

# Function to fetch data from the API
def fetch_data(change_order):
    url = API_URL_PATTERN.format(change_order)
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        data = response.json()
        return data
    return None

# Function to prepare data for raw_responses
def prepare_data(change_order_numbers):
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_change_order = {executor.submit(fetch_data, change_order): change_order for change_order in change_order_numbers}
        for future in as_completed(future_to_change_order):
            change_order = future_to_change_order[future]
            try:
                data = future.result()
                if data:
                    raw_responses.append(data)
            except Exception as exc:
                print(f"{change_order} generated an exception: {exc}")
    # Sort raw responses by scheduleStartDate
    raw_responses.sort(key=lambda x: datetime.strptime(x['scheduledStartDate'], ("%Y-%m-%d %H:%M:%S")) if 'scheduledStartDate' in x else datetime.min)

# Function to print table
def print_table(data):
    headers = ["Change Request", "Status", "Summary", "Schedule Start Date", "Implementer", "Pending Approvals", "Approved Groups"]
    rows = [
        [
            row['changeRequest'],
            row['status'],
            "\n".join(textwrap.wrap(row['summary'], width=20)),
            row['scheduleStartDate'],
            row['implementer'],
            row['pendingApprovals'],
            row['approvedGroups'] if row['status'].lower() not in ['review', 'close', 'closed'] else ''
        ]
        for row in data
    ]
    print(tabulate(rows, headers=headers, tablefmt='grid'))

# Prepare data for raw_responses
prepare_data(change_order_numbers)

# Process raw_responses to comprehensive_data and brief_summary_data
for data in raw_responses:
    if data.get('statusCode') == 200:
        result = data  # Assuming the data is directly in the response, not under 'result'
        comprehensive_data.append(result)
        
        # Create brief summary
        approvals = result['approvals']
        approval_status = {approval['approvalGroup']: approval['approvalStatus'] for approval in approvals}
        pending_approvals = [group for group, status in approval_status.items() if not status]
        approved_groups = [group for group, status in approval_status.items() if status == 'Approved']
        brief_summary_data.append({
            'changeRequest': result['changeRequest'],
            'status': result['status'],
            'summary': result['summary'],
            'scheduleStartDate': result['scheduledStartDate'],
            'scheduledEndDate': result.get('scheduledEndDate', ''),
            'implementer': result['implementer'],
            'pendingApprovals': "\n".join(pending_approvals),
            'approvedGroups': "\n".join(approved_groups) if result['status'].lower() not in ['review', 'close', 'closed'] else '',
            'snowURL': result.get('snowURL', '')
        })

# Write comprehensive data to CSV
with open('comprehensive_report.csv', 'w', newline='', encoding='utf-8') as file:
    fieldnames = list(comprehensive_data[0].keys()) + ['approvedGroups', 'pendingApprovals']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    for row in comprehensive_data:
        approvals = row.pop('approvals')
        approval_status = {approval['approvalGroup']: approval['approvalStatus'] for approval in approvals}
        row['pendingApprovals'] = "\n".join([group for group, status in approval_status.items() if not status])
        row['approvedGroups'] = "\n".join([group for group, status in approval_status.items() if status == 'Approved'])
        writer.writerow(row)

# Write brief summary data to CSV
with open('brief_summary_report.csv', 'w', newline='', encoding='utf-8') as file:
    fieldnames = ['changeRequest', 'status', 'summary', 'scheduleStartDate', 'scheduledEndDate', 'implementer', 'pendingApprovals', 'approvedGroups', 'snowURL']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(brief_summary_data)

# Write raw responses to a text file
with open('response_raw.txt', 'w', encoding='utf-8') as file:
    for response in raw_responses:
        file.write(json.dumps(response, indent=4, ensure_ascii=False))
        file.write('\n')

# Print brief summary to the screen in tabular format
print("\nBrief Summary Report:")
print_table(brief_summary_data)

# Read the data from the brief summary CSV and create an HTML file
with open('brief_summary_report.csv', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    rows = list(reader)

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Brief Summary Report</title>
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid black;
            padding: 8px;
            text-align: left;
            vertical-align: top;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <h1>Brief Summary Report</h1>
    <table>
        <thead>
            <tr>
                <th>Change Request</th>
                <th>Status</th>
                <th>Summary</th>
                <th>Schedule Start Date</th>
                <th>Scheduled End Date</th>
                <th>Implementer</th>
                <th>Pending Approvals</th>
                <th>Approved Groups</th>
                <th>Snow URL</th>
            </tr>
        </thead>
        <tbody>
"""
for row in rows:
    html_content += f"""
            <tr>
                <td>{row['changeRequest']}</td>
                <td>{row['status']}</td>
                <td>{row['summary']}</td>
                <td>{row['scheduleStartDate']}</td>
                <td>{row['scheduledEndDate']}</td>
                <td>{row['implementer']}</td>
                <td>{row['pendingApprovals'].replace('\n', '<br>')}</td>
                <td>{row['approvedGroups'].replace('\n', '<br>')}</td>
                <td>{row['snowURL']}</td>
            </tr>
    """
html_content += """
        </tbody>
    </table>
</body>
</html>
"""

# Write HTML content to file
with open('brief_summary_report.html', 'w', encoding='utf-8') as file:
    file.write(html_content)

# Open the HTML file in the default web browser
webbrowser.open('file://' + os.path.realpath('brief_summary_report.html'))
