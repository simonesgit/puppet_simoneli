def read_ad_groups(file_path):
    ad_groups = []

    # Read the file and store ad groups in a list
    with open(file_path, 'r') as file:
        for line in file:
            ad_group = line.strip()
            if ad_group:
                ad_groups.append(ad_group)

    # Remove duplicates from the list
    ad_groups = list(set(ad_groups))

    return ad_groups


# Provide the path to the adgroups.txt file
ad_groups_file = 'adgroups.txt'

# Read and process the ad groups
groups = read_ad_groups(ad_groups_file)

# Create a list to store the CSV data
csv_data = [['group', 'CN']]

# Call the CONNECT function for each group and store the output in the CSV data
for group in groups:
    members = CONNECT(group)
    for member in members:
        # Extract the CN value from the member string
        cn_value = member.split(',')[0]
        csv_data.append([group, cn_value])

# Save the CSV data to a file
output_file = 'output.csv'
with open(output_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(csv_data)

print(f"The output has been saved to {output_file}")
