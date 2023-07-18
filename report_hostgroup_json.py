import os
import json
import pandas as pd
import shutil

# Define the source paths
source_paths = ['\\server1\\agentgroup\\', '\\server2\\agentgroup\\', '\\server3\\agentgroup\\']

# Define the target path for source files
source_target_path = './source'

# Define the target path for raw files
raw_target_path = './raw'

# List to store file names
file_list = []

# Iterate over the source paths
for source_path in source_paths:
    # Get the list of files in the source path
    files = os.listdir(source_path)
    for file in files:
        # Check if the file matches the desired naming format
        if file.startswith('HOST-HOSTGROUP-MAPPING_') and file.endswith('.txt'):
            # Copy the file to the source target path
            source_file = os.path.join(source_path, file)
            target_file = os.path.join(source_target_path, file)
            shutil.copy(source_file, target_file)
            file_list.append(target_file)

# List to store the extracted data
data = []

# Iterate over the files in the raw target path
for file in file_list:
    with open(file, 'r') as f:
        json_data = json.load(f)
        
    # Iterate over the JSON data
    for key in json_data.keys():
        region, DCname = key.split('|')
        hostgroup = json_data[key][0]['hostGroupName']
        agents = json_data[key][0]['agents']
        
        # Iterate over the agents and create a row for each
        for agent in agents:
            data.append([region, DCname, hostgroup, agent])

# Create a dataframe from the extracted data
df = pd.DataFrame(data, columns=['region', 'dataCenter', 'hostgroup', 'agent'])

# Print the dataframe
print(df)
