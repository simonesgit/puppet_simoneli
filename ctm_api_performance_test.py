import requests
import json
import threading
import time
from datetime import datetime

# Configuration
base_url = "https://ctmapi.bmc.com:8441/automation-api"
api_login = "/session/login"
api_getdc = "/config/servers"
api_logout = "/session/logout"
fqdn_nodes = ["server_fqdn1", "server_fqdn2", "server_fqdn3"]
username = "your_username"
password = "your_password"
num_requests = 10  # Number of GET requests to make per node

# Results storage
results = {}
lock = threading.Lock()

def login_and_get_token():
    url = f"{base_url}{api_login}"
    response = requests.post(url, json={"username": username, "password": password})
    data = response.json()
    token = data.get("token")
    return token, response.status_code

def get_dc(node, token):
    url = f"https://{node}:8441/automation-api{api_getdc}"
    headers = {"Authorization": f"Bearer {token}"}
    response_times = []
    success_count = 0
    fail_count = 0
    responses = []

    start_node_time = datetime.now()

    for _ in range(num_requests):
        start_time = time.time()
        response = requests.get(url, headers=headers)
        end_time = time.time()

        response_time = (end_time - start_time) * 1000  # in milliseconds
        response_times.append(response_time)
        responses.append({
            "status_code": response.status_code,
            "response_time": response_time
        })

        if response.status_code == 200:
            success_count += 1
        else:
            fail_count += 1

    avg_response_time = sum(response_times) / len(response_times)
    total_response_time = sum(response_times)

    end_node_time = datetime.now()

    with lock:
        results[node] = {
            "responses": responses,
            "average_response_time": avg_response_time,
            "total_response_time": total_response_time,
            "success_count": success_count,
            "fail_count": fail_count,
            "start_node_time": start_node_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_node_time": end_node_time.strftime("%Y-%m-%d %H:%M:%S")
        }

def logout(token):
    url = f"{base_url}{api_logout}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, headers=headers)
    return response.status_code

def main():
    start_time = datetime.now()
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

    end_time = datetime.now()
    
    # Print results
    for node, result in results.items():
        print(f"\nServer Node: {node}")
        print(f"Node Test Start Time: {result['start_node_time']}")
        print(f"Node Test End Time: {result['end_node_time']}")
        for idx, res in enumerate(result["responses"], start=1):
            print(f"- Request {idx}: Status Code: {res['status_code']}, Response Time: {res['response_time']:.2f}ms")
        print(f"- Average Response Time: {result['average_response_time']:.2f}ms")
        print(f"- Total Response Time: {result['total_response_time']:.2f}ms")
        print(f"- Success Count: {result['success_count']}")
        print(f"- Fail Count: {result['fail_count']}")

    # Summary
    print("\nSummary:")
    for node, result in results.items():
        print(f"{node} - Average Response Time: {result['average_response_time']:.2f}ms, "
              f"Total Response Time: {result['total_response_time']:.2f}ms, "
              f"Success: {result['success_count']}, Fail: {result['fail_count']}")

    # Write raw results to file
    timestamp = start_time.strftime("%Y%m%d%H%M")
    with open(f"performance_test_raw_{timestamp}.txt", "w") as f:
        json.dump(results, f, indent=4)

    # Create HTML report
    with open(f"performance_test_report_{timestamp}.html", "w") as f:
        f.write("<!DOCTYPE html>")
        f.write("<html lang='en'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>")
        f.write("<title>Performance Test Result</title><style>")
        f.write("body { font-family: Arial, sans-serif; margin: 20px; }")
        f.write("h1 { color: #333; } h2 { color: #555; } p { color: #666; }")
        f.write("ul { list-style-type: none; padding: 0; } li { margin: 5px 0; } hr { margin: 20px 0; }")
        f.write("table { width: 100%; border-collapse: collapse; margin-top: 20px; }")
        f.write("th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }")
        f.write("th { background-color: #f2f2f2; }")
        f.write("</style></head><body>")
        f.write(f"<h1>Performance Test Result</h1>")
        f.write(f"<p>Test Start Time: {start_time}</p>")
        f.write(f"<p>Test End Time: {end_time}</p><hr>")

        for node, result in results.items():
            f.write(f"<h2>Server Node: {node}</h2>")
            f.write(f"<p>Node Test Start Time: {result['start_node_time']}</p>")
            f.write(f"<p>Node Test End Time: {result['end_node_time']}</p>")
            f.write("<ul>")
            for idx, res in enumerate(result["responses"], start=1):
                f.write(f"<li>Request {idx}: Status Code: {res['status_code']}, Response Time: {res['response_time']:.2f}ms</li>")
            f.write("</ul>")
            f.write(f"<p>Average Response Time: {result['average_response_time']:.2f}ms</p>")
            f.write(f"<p>Total Response Time: {result['total_response_time']:.2f}ms</p>")
            f.write(f"<p>Success Count: {result['success_count']}</p>")
            f.write(f"<p>Fail Count: {result['fail_count']}</p><hr>")

        f.write("<h2>Summary</h2>")
        f.write("<table><tr><th>Server Node</th><th>Average Response Time (ms)</th><th>Total Response Time (ms)</th>")
        f.write("<th>Success Count</th><th>Fail Count</th></tr>")
        for node, result in results.items():
            f.write(f"<tr><td>{node}</td><td>{result['average_response_time']:.2f}</td>")
            f.write(f"<td>{result['total_response_time']:.2f}</td><td>{result['success_count']}</td>")
            f.write(f"<td>{result['fail_count']}</td></tr>")
        f.write("</table></body></html>")

if __name__ == "__main__":
    main()
