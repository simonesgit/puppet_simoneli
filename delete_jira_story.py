import requests

def delete_jira_issues(api_url, auth, issue_ids):
    for issue_id in issue_ids:
        # Set the request URL
        url = f"{api_url}/issue/{issue_id}"

        # Send the request to delete the issue
        response = requests.delete(url, auth=auth)

        # Check the response status code
        if response.status_code == 204:
            print(f"Issue {issue_id} deleted successfully.")
        else:
            print(f"Failed to delete issue {issue_id}. Status code: {response.status_code}")


# JIRA API configuration
api_url = "https://your-jira-url/rest/api/latest"
username = "your-username"
password = "your-password"

# Read issue IDs from file
with open("source.txt", "r") as file:
    issue_ids = [line.strip() for line in file]

# Delete the issues
delete_jira_issues(api_url, (username, password), issue_ids)
