import requests

def update_confluence_page_content(space_key, page_id=None, page_title=None, username=None, password=None):
    # Set the Confluence API endpoint
    api_url = f"https://your-confluence-url/rest/api/content/{page_id or page_title}"

    # Set the request headers
    headers = {
        "Content-Type": "application/json"
    }

    # Set the request parameters
    params = {
        "spaceKey": space_key
    }

    # Read the new page content from the file
    with open("confluence_page_content.txt", "r", encoding="utf-8") as file:
        new_content = file.read()

    # Create the request payload
    payload = {
        "version": {
            "number": 1  # Increment the version number to update the page
        },
        "title": page_title,  # Only needed if updating by title
        "type": "page",
        "body": {
            "storage": {
                "value": new_content,
                "representation": "storage"
            }
        }
    }

    # Send the request to update page content
    response = requests.put(api_url, headers=headers, params=params, auth=(username, password), json=payload, verify="ca.pem")
    response.raise_for_status()

# Usage example
update_confluence_page_content(space_key="your-space-key", page_id="12345", username="your-username", password="your-password")
