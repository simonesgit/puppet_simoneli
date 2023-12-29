import pandas as pd

# Load the Excel file
df = pd.read_excel('path_to_your_file.xlsx', sheet_name='Sheet1', header=None)

# Assuming the first column (key) is column 0 and the second column (values) is column 1
# Split the values by comma and then explode the DataFrame to have each value on a separate row
df[1] = df[1].str.split(',')
df_exploded = df.explode(1)

# Rename the columns for clarity
df_exploded.columns = ['Key', 'Value']

# Save the reorganized DataFrame to a new Excel file
df_exploded.to_excel('path_to_new_file.xlsx', index=False)
