import os
import shutil
import bz2
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
    
skip_existing_files = True

# Loop through each file and download it to the local disk
failed_files = []
downloaded_files = []  # Added a list to store downloaded file information
for file_info in file_list:
    try:
        # Copy the file to the local disk with the region prefix
        dest_filename = f"{file_info['region']}_{os.path.basename(file_info['file'])}"
        dest_path = os.path.join('./source', dest_filename)

        # Check if the file already exists in the './source' directory and skip the download if it does
        if os.path.isfile(dest_path) and skip_existing_files:
            print(f"Skipped file {file_info['file']} because it already exists in {dest_path}")
        else:
            if not os.path.isfile(dest_path):
                shutil.copy(file_info['file'], dest_path)
                print(f"Downloaded file {file_info['file']} to {dest_path}")
            else:
                print(f"File {file_info['file']} already exists in {dest_path}")
            
        # Append the file information to the downloaded_files list, whether it was downloaded or already existed
        downloaded_files.append({'region': file_info['region'], 'date': file_info['date'], 'file': dest_path})
        
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

# Output the list of downloaded file information
print("Downloaded files information:")
for info in downloaded_files:
    print(info)

audit_roles = ['role1', 'role2', 'role3']
audit_accounts = []
ad_groups = []

for file_info in downloaded_files:
    with bz2.open(file_info['file'], 'rt') as f:
        for line in f:
            account, role, ad_group, description = line.strip().split(',')

            if role in audit_roles:
                # Update audit_accounts
                account_info = next((item for item in audit_accounts if item['account'] == account), None)
                if account_info:
                    if role not in account_info['acc_roles'].split(','):
                        account_info['acc_roles'] += f",{role}"
                else:
                    audit_accounts.append({'account': account, 'acc_roles': role})

                # Update ad_groups
                role_info = next((item for item in ad_groups if item['role'] == role), None)
                if role_info:
                    if ad_group not in role_info['ad_group'].split(','):
                        role_info['ad_group'] += f",{ad


audit_roles = ['role1', 'role2', 'role3']

audit_accounts = defaultdict(set)
ad_groups = defaultdict(set)

# Loop through the downloaded files
for file_info in downloaded_files:
    # Open and read the contents of the bz2 file
    with bz2.open(file_info['file'], 'rt') as f:
        # Process each line in the file
        for line in f:
            # Split the line by comma
            account, role, ad_group, description = line.strip().split(',')

            # Check if the role is in the audit_roles list
            if role in audit_roles:
                # Add the role to the audit_accounts dictionary
                audit_accounts[account].add(role)

                # Add the ad_group to the ad_groups dictionary
                ad_groups[role].add(ad_group)

# Convert the sets to comma-separated strings and store the results in lists
audit_accounts = [{'account': account, 'acc_roles': ','.join(roles)} for account, roles in audit_accounts.items()]
ad_groups = [{'role': role, 'ad_group': ','.join(groups)} for role, groups in ad_groups.items()]

# Output the extracted information
print("\nAudit accounts:")
for info in audit_accounts:
    print(info)

print("\nAD groups:")
for info in ad_groups:
    print(info)

