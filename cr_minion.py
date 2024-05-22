import csv
import json
import requests

# Define the API URL pattern
API_URL_PATTERN = "https://cp-mInion.uk.ccc/apl/v3/read?changeRequest={}&withChangeTasks=false&withPamTasks=false"

# Read change order numbers from CSV file
with open('change_orders.csv', 'r') as file:
    change_order_numbers = [line.strip() for line in file]

# Initialize lists to store data
comprehensive_data = []
brief_summary_data = []
raw_responses = []

# Fetch data from the API for each change order number
for change_order in change_order_numbers:
    print(f"Fetching data for change order: {change_order}")
    url = API_URL_PATTERN.format(change_order)
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        data = response.json()
        raw_responses.append(data)
        if data['status'] == 'success':
            result = data['result']
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
                'implementer': result['implementer'],
                'pendingApprovals': "\n".join(pending_approvals),
                'approvedGroups': "\n".join(approved_groups)
            })

# Write comprehensive data to CSV
with open('comprehensive_report.csv', 'w', newline='') as file:
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
with open('brief_summary_report.csv', 'w', newline='') as file:
    fieldnames = ['changeRequest', 'status', 'summary', 'scheduleStartDate', 'implementer', 'pendingApprovals', 'approvedGroups']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(brief_summary_data)

# Write raw responses to a text file
with open('response_raw.txt', 'w') as file:
    for response in raw_responses:
        file.write(json.dumps(response, indent=4))
        file.write('\n')

# Print brief summary to the screen in text format
print("\nBrief Summary Report:")
for row in brief_summary_data:
    print(f"\nChange Request: {row['changeRequest']}")
    print(f"Status: {row['status']}")
    print(f"Summary: {row['summary']}")
    print(f"Schedule Start Date: {row['scheduleStartDate']}")
    print(f"Implementer: {row['implementer']}")
    print(f"Approved Groups: {row['approvedGroups']}")
    print(f"Pending Approvals: {row['pendingApprovals']}")
