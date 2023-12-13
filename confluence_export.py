import requests

def get_confluence_page_content(space_key, page_id=None, page_title=None, username=None, password=None):
    # Set the Confluence API endpoint
    api_url = "https://your-confluence-url/rest/api/content"

    # Set the request headers
    headers = {
        "Accept": "application/json"
    }

    # Set the request parameters
    params = {
        "spaceKey": space_key
    }

    # Determine if the page ID or title is provided
    if page_id:
        params["pageId"] = page_id
    elif page_title:
        params["title"] = page_title

    # Send the request to get page content
    response = requests.get(api_url, headers=headers, params=params, auth=(username, password), verify="ca.pem")
    response.raise_for_status()

    # Extract the page content from the response
    page_content = response.json()["results"][0]["body"]["storage"]["value"]

    # Store the page content in a file
    with open("confluence_page_content.txt", "w", encoding="utf-8") as file:
        file.write(page_content)

# Usage example
get_confluence_page_content(space_key="your-space-key", page_id="12345", username="your-username", password="your-password")
