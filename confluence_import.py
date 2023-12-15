import requests

# Confluence API endpoint for retrieving and updating page content
api_url = 'https://your-confluence-site/wiki/rest/api/content/{page_id}'

# Page ID of the page you want to update
page_id = '12345678'

# Retrieve the existing page version
response = requests.get(api_url.format(page_id=page_id))
if response.status_code == 200:
    existing_version = response.json().get('version', {}).get('number', 0)
else:
    print(f'Failed to retrieve existing page version. Status code: {response.status_code}. Error message: {response.text}')
    existing_version = 0

# Prepare the API request payload
payload = {
    'version': {
        'number': existing_version + 1  # Increase the existing version number to update the content
    },
    'body': {
        'storage': {
            'value': html_content,
            'representation': 'storage'
        }
    }
}

# Make the API request
response = requests.put(api_url.format(page_id=page_id), json=payload, headers={'Content-Type': 'application/json'})

# Check the response status
if response.status_code == 200:
    print('Page content updated successfully.')
else:
    print(f'Failed to update page content. Status code: {response.status_code}. Error message: {response.text}')
