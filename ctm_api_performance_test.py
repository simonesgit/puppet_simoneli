import requests
import json
import threading
import time
from datetime import datetime
import pytz
import webbrowser

# Load environment profile
env_profile = "HK_UAT.json"
profile_name = env_profile.rstrip('.json')

with open(env_profile, 'r') as f:
    config = json.load(f)

# Configuration from profile with inline conditional assignments
base_url = config.get("base_url")
api_login = config.get("api_login")
api_getdc = config.get("api_getdc")
api_logout = config.get("api_logout")
fqdn_nodes = config.get("fqdn_nodes")
username = config.get("username") if config.get("username") else "your_username"
password = config.get("password") if config.get("password") else "your_password"
num_requests = config.get("num_requests", 10)
ca_file = config.get("ca_file") if config.get("ca_file") else "HHHHTree.pem"
timezone = config.get("timezone", "HKT")

# Timezone conversion
timezone_mapping = {
    "HKT": "Asia/Hong_Kong",
    "GBT": "Europe/London",
    "CST": "America/Chicago"
}

local_tz = pytz.timezone(timezone_mapping.get(timezone, "UTC"))

# Results storage
results = {}
lock = threading.Lock()

def convert_to_local_time(utc_time):
    return utc_time.astimezone(local_tz)

def login_and_get_token():
    url = f"{base_url}{api_login}"
    try:
        response = requests.post(url, json={"username": username, "password": password}, verify=ca_file)
        data = response.json()
        token = data.get("token")
        return token, response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Login failed: {e}")
        return None, 500

def get_dc(node, token):
    url = f"https://{node}:8441/automation-api{api_getdc}"
    headers = {"Authorization": f"Bearer {token}"}
    response_times = []
    success_count = 0
    fail_count = 0
    responses = []

    start_node_time = datetime.now(pytz.utc)

    for _ in range(num_requests):
        try:
            start_time = time.time()
            response = requests.get(url, headers=headers, verify=ca_file)
            end_time = time.time()

            response_time = (end_time - start_time) * 1000  # in milliseconds
            response_times.append(response_time)
            responses.append({
                "status_code": response.status_code,
                "response_time": response_time,
                "response_json": response.json()
            })

            if response.status_code == 200:
                success_count += 1
            else:
                fail_count += 1

        except requests.exceptions.RequestException as e:
            response_times.append(0)
            fail_count += 1
            responses.append({
                "status_code": 500,
                "response_time": 0,
                "response_json": {"error": str(e)}
            })

    avg_response_time = sum(response_times) / len(response_times)
    total_response_time = sum(response_times)

    end_node_time = datetime.now(pytz.utc)

    with lock:
        results[node] = {
            "responses": responses,
            "average_response_time": avg_response_time,
            "total_response_time": total_response_time,
            "success_count": success_count,
            "fail_count": fail_count,
            "start_node_time": convert_to_local_time(start_node_time).strftime("%Y-%m-%d %H:%M:%S %Z"),
            "end_node_time": convert_to_local_time(end_node_time).strftime("%Y-%m-%d %H:%M:%S %Z")
        }

    print(f"Test completed for node: {node}")

def logout(token):
    url = f"{base_url}{api_logout}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(url, headers=headers, verify=ca_file)
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Logout failed: {e}")
        return 500

def main():
    start_time = datetime.now(pytz.utc)
    token, login_status = login_and_get_token()
    
    if login_status != 200:
        print("Login failed!")
        return
    
    print(f"Login API Response: Status Code: {login_status}")
    
    threads = []
    for node in fqdn_nodes:
        thread = threading.Thread(target=get_dc, args=(node, token))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

    logout_status = logout(token)
    print(f"Logout API Response: Status Code: {logout_status}")

    end_time = datetime.now(pytz.utc)
    
    # Summary
    print("\nSummary:")
    for node in fqdn_nodes:
        result = results[node]
        print(f"{node} - Average Response Time: {result['average_response_time']:.2f}ms, "
              f"Total Response Time: {result['total_response_time']:.2f}ms, "
              f"Success: {result['success_count']}, Fail: {result['fail_count']}")

    # Print results
    for node in fqdn_nodes:
        result = results[node]
        print(f"\nServer Node: {node}")
        print(f"Node Test Start Time: {result['start_node_time']}")
        print(f"Node Test End Time: {result['end_node_time']}")
        for idx, res in enumerate(result["responses"], start=1):
            print(f"- Request {idx}: Status Code: {res['status_code']}, Response Time: {res['response_time']:.2f}ms")
        print(f"- Average Response Time: {result['average_response_time']:.2f}ms")
        print(f"- Total Response Time: {result['total_response_time']:.2f}ms")
        print(f"- Success Count: {result['success_count']}")
        print(f"- Fail Count: {result['fail_count']}")

    # Write raw results to file
    timestamp = start_time.strftime("%Y%m%d%H%M")
    report_filename = f"{profile_name}_performance_test_report_{timestamp}.html"
    
    with open(f"{profile_name}_performance_test_raw_{timestamp}.txt", "w") as f:
        json.dump(results, f, indent=4)

    # Create HTML report
    with open(report_filename, "w") as f:
        f.write("<!DOCTYPE html>")
        f.write("<html lang='en'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>")
        f.write("<title>Control-M Automation API Performance Test Result</title><style>")
        f.write("body { font-family: Arial, sans-serif; margin: 20px; }")
        f.write("h1 { color: #333; } h2 { color: #555; } p { color: #666; }")
        f.write("ul { list-style-type: none; padding: 0; } li { margin: 5px 0; } hr { margin: 20px 0; }")
        f.write("table { width: 100%; border-collapse: collapse; margin-top: 20px; }")
        f.write("th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }")
        f.write("th { background-color: #f2f2f2; }")
        f.write("details { margin-bottom: 10px; }")
        f.write("details pre { background-color: #f9f9f9; padding: 10px; border-radius: 5px; white-space: pre-wrap; word-wrap: break-word; }")
        f.write("</style></head><body>")
        f.write(f"<h1>Control-M Automation API Performance Test Result</h1>")
        f.write(f"<p><strong>Test AAPI Profile: {profile_name}</strong></p>")
        f.write(f"<p><strong>Test AAPI end-point: {api_getdc}</strong></p>")
        f.write(f"<p>Test Start Time: {convert_to_local_time(start_time).strftime('%Y-%m-%d %H:%M:%S %Z')}</p>")
        f.write(f"<p>Test End Time: {convert_to_local_time(end_time).strftime('%Y-%m-%d %H:%M:%S %Z')}</p><hr>")

        f.write("<h2>Summary</h2>")
        f.write("<table><tr><th>Server Node</th><th>Average Response Time (ms)</th><th>Total Response Time (ms)</th>")
        f.write("<th>Success Count</th><th>Fail Count</th></tr>")
        for node in fqdn_nodes:
            result = results[node]
            f.write(f"<tr><td>{node}</td><td>{result['average_response_time']:.2f}</td>")
            f.write(f"<td>{result['total_response_time']:.2f}</td><td>{result['success_count']}</td>")
            f.write(f"<td>{result['fail_count']}</td></tr>")
        f.write("</table><hr>")

        for node in fqdn_nodes:
            result = results[node]
            f.write(f"<h2>Server Node: {node}</h2>")
            f.write(f"<p>Node Test Start Time: {result['start_node_time']}</p>")
            f.write(f"<p>Node Test End Time: {result['end_node_time']}</p>")
            f.write("<ul>")
            for idx, res in enumerate(result["responses"], start=1):
                f.write(f"<details><summary>Request {idx}: Status Code: {res['status_code']}, Response Time: {res['response_time']:.2f}ms</summary>")
                f.write(f"<pre>{json.dumps(res['response_json'], indent=4)}</pre>")
                f.write("</details>")
            f.write("</ul>")
            f.write(f"<p>Average Response Time: {result['average_response_time']:.2f}ms</p>")
            f.write(f"<p>Total Response Time: {result['total_response_time']:.2f}ms</p>")
            f.write(f"<p>Success Count: {result['success_count']}</p>")
            f.write(f"<p>Fail Count: {result['fail_count']}</p><hr>")
        
        f.write("</body></html>")

    # Open the HTML report in the default web browser
    webbrowser.open(report_filename)

if __name__ == "__main__":
    main()
