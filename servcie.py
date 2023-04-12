import os
import shutil
from datetime import datetime, timedelta

# Define the source file paths
source_files = {'hk': '\\\\server\\pathhk', 'uk': '\\\\server2\\pathuk', 'us': '\\\\server3\\pathus'}

# Define the date range
date_from = datetime(2023, 3, 1)
date_to = datetime(2023, 4, 1)

# Define the list to store the file information
file_list = []

# Loop through each source file path
for region, path in source_files.items():
    # Loop through each date in the range
    current_date = date_from
    while current_date <= date_to:
        # Define the filename for the current date
        filename = f'backup_em_audit_{current_date.strftime("%Y%m%d")}.log.bz2'

        # Define the full path to the file
        file_path = os.path.join(path, filename)

        # Check if the file exists and is a file (not a directory)
        if os.path.isfile(file_path):
            # Add the file information to the list
            file_list.append({'region': region, 'date': current_date.strftime("%Y%m%d"), 'file': file_path})
        
        # Move to the next date
        current_date += timedelta(days=1)

# Create the sub-folder if it doesn't exist
if not os.path.exists('./source'):
    os.makedirs('./source')

# Loop through each file and download it to the local disk
failed_files = []
for file_info in file_list:
    try:
        # Copy the file to the local disk
        dest_path = os.path.join('./source', os.path.basename(file_info['file']))
        shutil.copy(file_info['file'], dest_path)
        
        # Print a success message
        print(f"Downloaded file {file_info['file']} to {dest_path}")
    except Exception as e:
        # Add the failed file to the list and print a warning message
        failed_files.append(file_info)
        print(f"WARNING: Failed to download file {file_info['file']}: {e}")

# Write the list of failed files to a log file
if failed_files:
    log_filename = f"./logs/history_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(log_filename, 'w') as log_file:
        for file_info in failed_files:
            log_file.write(f"Failed to download file {file_info['file']} for region {file_info['region']} on {file_info['date']}\n")
    print(f"WARNING: {len(failed_files)} files failed to download. See log file {log_filename} for details.")
else:
    print("All files downloaded successfully.")
