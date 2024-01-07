import requests
import json


def get_latest_comment(issue_key):
    # Read credentials from a file
    with open('credentials.txt', 'r') as file:
        credentials = json.load(file)

    # API endpoint
    api_url = f"https://your-jira-instance/rest/api/2/issue/{issue_key}/comment"

    # SSL verification using a PEM file
    pem_file = '/path/to/your/pem/file.pem'

    # Make the API request
    response = requests.get(api_url, headers={'Content-Type': 'application/json'},
                            auth=(credentials['username'], credentials['password']), verify=pem_file)

    if response.status_code == 200:
        # Parse the response
        comments = response.json()['comments']
        latest_comment = comments[-1]['body'] if comments else "No comments found."
        return latest_comment
    else:
        return f"Error: {response.status_code} - {response.text}"


if __name__ == '__main__':
    # Main function
    def main():
        issue_key = input("Enter the issue key: ")
        latest_comment = get_latest_comment(issue_key)
        print(f"The latest comment for issue {issue_key} is:\n{latest_comment}")

    # Call the main function
    main()
