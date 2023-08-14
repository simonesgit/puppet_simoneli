import pandas as pd

# Create the original dataframe
data = {
    'HLQ': ['AAA', 'AAA', 'AAA', 'BBB', 'CCC', 'DDD'],
    'EIMID': [123, 124, 125, 125, 126, 126]
}
df_result_final = pd.DataFrame(data)

# Logic to process the dataframe

# Get the count of unique HLQ-EIMID combinations
count_df = df_result_final.groupby('EIMID')['HLQ'].nunique().reset_index(name='Count')

# Filter count dataframe where count is equal to 1 and sort by HLQ
new_dataframe = count_df[count_df['Count'] == 1].sort_values(by='EIMID')

# Merge new dataframe with original dataframe to filter rows
df_result_final = pd.merge(df_result_final, new_dataframe, on='EIMID')

# Print the result
print(df_result_final)
