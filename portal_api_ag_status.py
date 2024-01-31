import csv
import json
import requests

class AppStatusAPI:
    def __init__(self):
        self.base_url = "https://aaa.bb.com/v1/user/login"
        self.token = None

    def login(self, username, password):
        data = {
            "username": username,
            "password": password
        }
        response = requests.post(self.base_url, json=data)
        response_data = response.json()
        if response_data["code"] == 0:
            self.token = response_data["data"]
        else:
            raise Exception("Login failed: {}".format(response_data["msg"]))

    def renew_token(self):
        if self.token is None:
            raise Exception("Token is not set")
        
        # Implement token renewal logic here
        
    def get_agent_status(self, server, agent):
        if self.token is None:
            raise Exception("Token is not set")

        headers = {
            "x-hhhh-e2e-trust-token": self.token
        }
        url = "https://aa.bb.com/v1/ctm/hostnames/{}/agents/{}:?retry=N".format(server, agent)
        response = requests.get(url, headers=headers)
        response_data = response.json()
        if response_data["code"] == 0:
            return response_data["data"]["diagnosis"]
        else:
            raise Exception("API call failed: {}".format(response_data["msg"]))

def main():
    api = AppStatusAPI()
    
    # Read Jira credentials from JSON file
    with open('api_credentials.json', 'r') as file:
        credentials = json.load(file)
    
    # Create report file
    with open('ag_diag_comm_results.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['server', 'agent', 'api_rc', 'diag_comm'])
        writer.writeheader()
        
        # Read server list from file
        with open('servers.csv', 'r') as server_file:
            reader = csv.DictReader(server_file)
            servers = list(reader)
        
        # Iterate over servers and agents
        for server in servers:
            try:
                api.login(credentials["username"], credentials["password"])
                diag_comm = api.get_agent_status(server['server'], server['agent'])
                writer.writerow({
                    'server': server['server'],
                    'agent': server['agent'],
                    'api_rc': 'Success',
                    'diag_comm': diag_comm
                })
            except Exception as e:
                writer.writerow({
                    'server': server['server'],
                    'agent': server['agent'],
                    'api_rc': 'Failed',
                    'diag_comm': str(e)
                })

if __name__ == "__main__":
    main()
