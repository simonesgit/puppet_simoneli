import requests

# Confluence API endpoint for retrieving and updating page content
api_url = 'https://your-confluence-site/wiki/rest/api/content/{page_id}'

# Page ID of the page you want to update
page_id = '12345678'

# Credentials for authentication
username = 'your-username'
password = 'your-password'

# Path to the CA certificate file for SSL verification
ca_cert_path = '/path/to/ca.pem'

# Function to retrieve the current version of the page
def get_page_version():
    response = requests.get(api_url.format(page_id=page_id), auth=(username, password), verify=ca_cert_path)
    if response.status_code == 200:
        return response.json().get('version', {}).get('number', 0)
    else:
        print(f'Failed to retrieve existing page version. Status code: {response.status_code}. Error message: {response.text}')
        return 0

# Function to update the page content
def update_page_content(version, content):
    payload = {
        'version': {
            'number': version + 1  # Increase the existing version number to update the content
        },
        'body': {
            'storage': {
                'value': content,
                'representation': 'storage'
            }
        }
    }
    response = requests.put(api_url.format(page_id=page_id), json=payload, auth=(username, password), verify=ca_cert_path, headers={'Content-Type': 'application/json'})
    if response.status_code == 200:
        print('Page content updated successfully.')
    else:
        print(f'Failed to update page content. Status code: {response.status_code}. Error message: {response.text}')

# Read the HTML content from file
with open('project.html', 'r') as file:
    html_content = file.read()

# Get the current version of the page
current_version = get_page_version()

# Update the page content
update_page_content(current_version, html_content)
