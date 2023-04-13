# Assuming you have a DataFrame called df
columns_to_rename = ['old_column_name1', 'old_column_name2']  # Replace with the column names you want to rename
new_column_names = ['new_column_name1', 'new_column_name2']  # Replace with the desired new column names

# Create a dictionary to map old column names to new column names only for the columns in columns_to_rename
column_mapping = {old: new for old, new in zip(columns_to_rename, new_column_names)}

# Rename columns using the column_mapping dictionary
df = df.rename(columns=column_mapping)
