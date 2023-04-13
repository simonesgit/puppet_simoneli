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

ad_groups2 = []
for role, groups in ad_groups.items():
    for group in groups:
        ad_groups2.append({'role': role, 'ad_group': group})

# Output the extracted information
print("\nAudit accounts:")
for info in audit_accounts:
    print(info)

print("\nAD groups:")
for info in ad_groups:
    print(info)

print("\nAD groups2:")
for info in ad_groups2:
    print(info)



import io
import bz2

def process_em_logs(raw_log_em, audit_accounts, date_from, date_to):
    # Create an empty dataframe to store the logs
    logs_df = pd.DataFrame()

    # Get the list of target accounts
    target_accounts = [account_info['account'] for account_info in audit_accounts]

    # Process each file in raw_log_em
    for file_info in raw_log_em:
        # Read and decode the bz2 file content with utf-8
        with bz2.open(file_info['file'], mode='rt', encoding='utf-8') as file:
            content = file.read()

        # Replace quotes and remove spaces around '|'
        content = content.replace('"', '').replace(' |', '|').replace('| ', '|')

        # Remove lines containing only '='
        content = '\n'.join([line for line in content.split('\n') if not set(line.strip()) == {'='}])

        # Read the processed content directly into a dataframe using io.StringIO
        file_df = pd.read_csv(io.StringIO(content), sep='|', engine='python')

        # Filter the rows based on target_accounts
        filtered_df = file_df[file_df['Username'].isin(target_accounts)]

        # Append the filtered dataframe to the logs dataframe
        logs_df = logs_df.append(filtered_df, ignore_index=True)

    # Save the logs dataframe to a CSV file
    csv_filename = f"em_audit_logs_{date_from.strftime('%Y%m%d')}_{date_to.strftime('%Y%m%d')}.csv"
    logs_df.to_csv(csv_filename, index=False)

    return logs_df
   
def download_files(source_paths, pattern, date_from, date_to, skip_existing_files=True):
    file_list = []

    if skip_existing_files:
        files_in_source = os.listdir('./source')
        all_dates_covered = True

        for region in source_paths.keys():
            for current_date in (date_from + timedelta(days=n) for n in range((date_to - date_from).days + 1)):
                date_string = current_date.strftime("%Y%m%d")
                matching_files = [file for file in files_in_source if f"{region}_{pattern}_{date_string}" in file]

                if not matching_files:
                    all_dates_covered = False
                    break

            if not all_dates_covered:
                break

        if all_dates_covered:
            for region in source_paths.keys():
                for current_date in (date_from + timedelta(days=n) for n in range((date_to - date_from).days + 1)):
                    date_string = current_date.strftime("%Y%m%d")
                    matching_file = next(file for file in files_in_source if f"{region}_{pattern}_{date_string}" in file)
                    file_list.append({'region': region, 'date': date_string, 'file': os.path.join('./source', matching_file)})

    if not file_list:
        for region, path in source_paths.items():
            region_files = []

            for root, _, files in os.walk(path):
                for filename in files:
                    if pattern in filename:
                        for current_date in (date_from + timedelta(days=n) for n in range((date_to - date_from).days + 1)):
                            if current_date.strftime("%Y%m%d") in filename:
                                region_files.append({'region': region, 'date': current_date.strftime("%Y%m%d"), 'file': os.path.join(root, filename)})

            if not region_files:
                loginfo = f"WARNING: No matching files found for region {region} and date range {date_from.strftime('%Y%m%d')} to {date_to.strftime('%Y%m%d')}"
                logger(loginfo)
            else:
                file_list.extend(region_files)

    downloaded_files = []

    if not os.path.exists('./source'):
        os.makedirs('./source')

    for file_info in file_list:
        dest_path = os.path.join('./source', f"{file_info['region']}_{os.path.basename(file_info['file'])}")

        if not os.path.exists(dest_path):
            try:
                shutil.copy(file_info['file'], dest_path)
                print(f"Downloaded file {file_info['file']} to {dest_path}")
            except Exception as e:
                loginfo = f"WARNING: Failed to download file {file_info['file']}: {e}"
                logger(loginfo)

        downloaded_files.append({'region': file_info['region'], 'date': file_info['date'], 'file': dest_path})

    return downloaded_files

import pandas as pd
import zipfile
import os

def logger(loginfo):
    print(loginfo)

def process_tpam_logs(raw_tpam_logs, audited_accounts, date_from, date_to):
    all_data = []
    target_accounts = [acc['account'] for acc in audited_accounts]

    for i, log in enumerate(raw_tpam_logs):
        try:
            with zipfile.ZipFile(log['file'], 'r') as zip_ref:
                possible_files = ['PasswordReleasedActivity.csv', 'UnixPasswordReleasedActivity.csv']
                target_file = None

                for file in possible_files:
                    if file in zip_ref.namelist():
                        target_file = file
                        break

                if target_file is None:
                    loginfo = f"WARNING: Can't identify the logs file inside the file named {log['file']}"
                    logger(loginfo)
                    continue

                with zip_ref.open(target_file) as file:
                    df = pd.read_csv(file, encoding="ISO-8859-1")
                    df = df[df['AccountName'].isin(target_accounts)]
                    all_data.append(df)
        except Exception as e:
            loginfo = f"WARNING: Failed to process file {log['file']}: {e}"
            logger(loginfo)

        # Print progress
        progress = (i + 1) / len(raw_tpam_logs) * 100
        print(f"Progress: {progress:.2f}%")

    if all_data:
        result = pd.concat(all_data, ignore_index=True)
        output_file = f"tpam_audit_logs_{date_from.strftime('%Y%m%d')}_{date_to.strftime('%Y%m%d')}.csv"
        result.to_csv(output_file, index=False)
        print(f"Data saved to {output_file}")
        return result
    else:
        print("No data to process.")
        return None
emlogs['TicketNbr'] = emlogs['USER_NOTE'].str.extract(r'(?P<TicketNbr>in\d+)')

# Now, merge both DataFrames on the TicketNbr column
merged_df = pd.merge(emlogs, tpamlogs, on='TicketNbr', how='outer')
