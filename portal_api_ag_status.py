import csv
import json
import requests
from tqdm import tqdm

class AppStatusAPI:
    def __init__(self, base_url, ca_cert_file, max_token_renewal_attempts=3):
        self.base_url = base_url
        self.ca_cert_file = ca_cert_file
        self.token = None
        self.max_token_renewal_attempts = max_token_renewal_attempts
        self.token_renewal_attempts = 0

    def login(self, username, password):
        data = {
            "username": username,
            "password": password
        }
        response = requests.post(self.base_url + "/v1/user/login", json=data, verify=self.ca_cert_file)
        response_data = response.json()
        if response_data["code"] == 0:
            self.token = response_data["data"]
        elif response_data["code"] == 50014:
            self.renew_token()
            self.login(username, password)
        else:
            raise Exception("Login failed: {}".format(response_data["msg"]))

    def renew_token(self):
        if self.token_renewal_attempts >= self.max_token_renewal_attempts:
            raise Exception("Maximum token renewal attempts reached")
        
        if self.token is None:
            raise Exception("Token is not set")
        
        # Implement token renewal logic here
        
        print("Token renewed")
        self.token_renewal_attempts += 1

    def get_agent_status(self, server, agent):
        if self.token is None:
            raise Exception("Token is not set")

        headers = {
            "x-hhhh-e2e-trust-token": self.token
        }
        url = self.base_url + "/v1/ctm/hostnames/{}/agents/{}?retry=N".format(server, agent)
        response = requests.get(url, headers=headers, verify=self.ca_cert_file)
        response_data = response.json()
        if response_data["code"] == 0:
            return response_data["data"]["diagnosis"], response_data["msg"]
        elif response_data["code"] == 50014:
            self.renew_token()
            return self.get_agent_status(server, agent)
        else:
            raise Exception("API call failed: {}".format(response_data["msg"]))

def main(is_production=False):
    # Choose the appropriate base URL
    if is_production:
        base_url = "https://aaa.bb.com"
    else:
        base_url = "https://uat.aa.bb.com"
    
    # Set the path to the CA certificate file
    ca_cert_file = "CATree.pem"
    
    api = AppStatusAPI(base_url, ca_cert_file)
    
    # Read Jira credentials from JSON file
    with open('api_credentials.json', 'r') as file:
        credentials = json.load(file)
    
    # Create report file
    with open('ag_diag_comm_results.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['server', 'agent', 'api_rc', 'api_msg', 'diag_comm'])
        writer.writeheader()
        
        # Read server list from file
        with open('servers.csv', 'r') as server_file:
            reader = csv.DictReader(server_file)
            servers = list(reader)
        
        total_servers = len(servers)
        completed_servers = 0
        
        # Use tqdm to display progress and estimate time to end
        with tqdm(total=total_servers, desc='Progress') as pbar:
            # Iterate over servers and agents
            for server in servers:
                try:
                    if api.token is None:
                        api.login(credentials["username"], credentials["password"])
                    diag_comm, api_msg = api.get_agent_status(server['server'], server['agent'])
                    writer.writerow({
                        'server': server['server'],
                        'agent': server['agent'],
                        'api_rc': 'Success',
                        'api_msg': api_msg,
                        'diag_comm': diag_comm
                    })
                    completed_servers += 1
                    pbar.update(1)
                    pbar.set_postfix({'API Response': 'Success', 'Message': api_msg})
                except Exception as e:
                    writer.writerow({
                        'server': server['server'],
                        'agent': server['agent'],
                        'api_rc': 'Failed',
                        'api_msg': str(e),
                        'diag_comm': ''
                    })
                    pbar.set_postfix({'API Response': 'Failed', 'Error': str(e)})
    
    # Calculate estimated time to end
    estimated_time = (total_servers - completed_servers) * 5  # Assuming 5 seconds per server
    print("Estimated time to end: {} seconds".format(estimated_time))

if __name__ == "__main__":
    is_production = False  # Set to True for production or False for UAT
    main(is_production)
