import requests
from bs4 import BeautifulSoup

# Replace <repository_url> with the actual URL of your repository
repository_url = "http://<repository_url>/repos/rhel/8/x86_64/"

response = requests.get(repository_url)
if response.status_code == 200:
    content = response.text

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")

    # Find all <a> tags which represent links
    links = soup.find_all("a")

    # Extract folder and file names from the links
    folder_and_file_names = []
    for link in links:
        name = link.get("href")
        if name.endswith("/"):  # If the name ends with a forward slash, it represents a folder
            folder_and_file_names.append(f"[Folder] {name}")
        else:
            folder_and_file_names.append(f"[File] {name}")

    # Store the list of folders and files to a local file
    output_file = "folder_and_file_list.txt"
    with open(output_file, "w") as file:
        file.write("\n".join(folder_and_file_names))

    print(f"List of folders and files under {repository_url} has been saved to {output_file}.")
else:
    print(f"Error: Failed to retrieve the repository content. Status code: {response.status_code}")
