import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Replace <repository_url> with the actual URL of your repository
repository_url = "https://<repository_url>/repos/rhel/8/x86_64/"

def get_folder_contents(url):
    response = requests.get(url, verify=True)
    if response.status_code == 200:
        content = response.text
        soup = BeautifulSoup(content, "html.parser")
        links = soup.find_all("a")

        folder_and_file_names = []
        for link in links:
            name = link.get("href")
            if name.endswith("/"):  # If the name ends with a forward slash, it represents a folder
                folder_url = urljoin(url, name)
                subfolder_contents = get_folder_contents(folder_url)
                folder_and_file_names.extend(subfolder_contents)
            else:
                folder_and_file_names.append(f"[File] {name}")

        return folder_and_file_names
    else:
        print(f"Error: Failed to retrieve the content of {url}. Status code: {response.status_code}")
        return []

# Starting point: list the contents of the root repository URL
folder_and_file_names = get_folder_contents(repository_url)

# Store the list of folders and files to a local file
output_file = "folder_and_file_list.txt"
with open(output_file, "w") as file:
    file.write("\n".join(folder_and_file_names))

print(f"List of folders and files under {repository_url} and its subfolders has been saved to {output_file}.")
