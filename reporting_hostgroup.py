import os
import pandas as pd
import bz2
from datetime import datetime, timedelta

# Define the source paths
source_paths = ['\\server1\\agentgroup\\', '\\server2\\agentgroup\\', '\\server3\\agentgroup\\']

# Define the target path for raw files
target_path = './raw'

# Calculate the date 2 days earlier
two_days_ago = datetime.now() - timedelta(days=2)
date_threshold = two_days_ago.strftime('%Y%m%d')

# List to store file names
file_list = []

# Iterate over the source paths
for source_path in source_paths:
    # Get the list of files in the source path
    files = os.listdir(source_path)
    for file in files:
        # Check if the file matches the desired date format
        if file.endswith('.csv.bz2') and file.split('_')[-1].split('.')[0] == date_threshold:
            # Copy the file to the target path
            source_file = os.path.join(source_path, file)
            target_file = os.path.join(target_path, file)
            shutil.copy(source_file, target_file)
            file_list.append(target_file)

# Read all bz2 files into a single dataframe
data = []
for file in file_list:
    with bz2.BZ2File(file, 'rb') as f:
        uncompressed_data = f.read().decode('utf-8')
    df = pd.read_csv(pd.compat.StringIO(uncompressed_data), header=None)
    # Add server and DCname columns
    server = os.path.dirname(file).split('\\')[2]
    DCname = file.split('_')[1]
    df['server'] = server
    df['DCname'] = DCname
    data.append(df)

# Concatenate all dataframes into a single dataframe
final_df = pd.concat(data, ignore_index=True)

# Rename columns
final_df.columns = ['c1', 'c2', 'c3', 'c4', 'c5', 'server', 'DCname']

# Print the final dataframe
print(final_df)
