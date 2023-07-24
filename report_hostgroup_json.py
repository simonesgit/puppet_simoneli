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
df_hhg = df

import pandas as pd
# Read the first sheet in the xlsx file into a dataframe
agent_inventory_file = r"HKUKUS_Agent_Inventory.xlsx"
df_agent = pd.read_excel(agent_inventory_file, sheet_name=0)

# Existing dataframe df_hhg (Assuming it is already defined)
# df_hhg = ...

# Perform a left join on df_hhg and df_agent based on the condition df_hhg.agent equals to df_agent.Object
df_hostname = df_hhg.merge(df_agent[['Region', 'Domain Class', 'Domain', 'Object Class', 'DC', 'Action']], 
                           how='left', left_on='agent', right_on='Object')

# Drop the 'Object' column from df_agent
df_hostname.drop('Object', axis=1, inplace=True)

# Create a new column 'HLQ' in df_hostname
df_hostname['HLQ'] = ''

# Update the 'HLQ' column in df_hostname based on hostgroup values
df_hostname.loc[df_hostname['hostgroup'].str.startswith(('P', 'L', 'N')) & 
                 df_hostname['hostgroup'].str[4].isin(['W', 'L']), 'HLQ'] = df_hostname['hostgroup'].str[:4]

df_hostname.loc[df_hostname['hostgroup'].str.startswith('CTMI'), 'HLQ'] = 'CTMI'

# Print the updated df_hostname
print(df_hostname)





import pandas as pd

# Read the df_hostname dataframe
df_hostname = pd.read_excel('TABLE_NODE.xlsx', sheet_name='All Data')

# Remove columns
columns_to_remove = ['Object Class', 'Action']
df_hostname = df_hostname.drop(columns=columns_to_remove)

# Rename columns
column_mapping = {
    'Domain Class': 'OSType',
    'Domain': 'hostname',
    'DC': 'Env'
}
df_hostname = df_hostname.rename(columns=column_mapping)

# Reorder columns
column_order = ['Env'] + [col for col in df_hostname.columns if col != 'Env']
df_hostname = df_hostname[column_order]

# Read the df_apphlq dataframe
df_apphlq = pd.read_excel('TABLE_NODE.xlsx', sheet_name='All Data')

# Create the FOLDER_HLQ column
def calculate_folder_hlq(sched_table):
    uppercase_sched_table = sched_table.upper()
    if uppercase_sched_table.startswith(('P', 'N', 'L')):
        return uppercase_sched_table[:4]
    elif uppercase_sched_table.startswith('CTM'):
        return uppercase_sched_table[:4]
    else:
        return None

df_apphlq['FOLDER_HLQ'] = df_apphlq['SCHED_TABLE'].apply(calculate_folder_hlq)

# Perform the left join
df_result = pd.merge(df_hostname, df_apphlq, how='left', left_on=['dataCenter', 'hostgroup'], right_on=['DATA_CENTER', 'NODE_ID'])

# Select the desired columns from df_apphlq
columns_to_select = ['APPLICATION', 'REGION', 'FOLDER_HLQ']
df_result = df_result[df_result.columns.union(columns_to_select)]

print(df_result)
