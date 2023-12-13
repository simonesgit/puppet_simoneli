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

# Print the unique ad groups
for group in groups:
    print(group)
