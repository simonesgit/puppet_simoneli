import requests

# Confluence API configuration
api_url = "https://your-confluence-url/rest/api"
username = "your-username"
password = "your-password"

# Page ID of the Confluence page
page_id = "12345678"  # Replace with the actual page ID

# Set the request URL
url = f"{api_url}/content/{page_id}?expand=body.storage"

# Send the request to retrieve the page content
response = requests.get(url, auth=(username, password))
response.raise_for_status()

# Extract the body content from the response
body_content = response.json()["body"]["storage"]["value"]

# Print the body content
print(body_content)
