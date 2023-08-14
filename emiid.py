import pandas as pd

# Create the original dataframe
data = {
    'HLQ': ['AAA', 'AAA', 'AAA', 'BBB', 'CCC', 'DDD'],
    'EIMID': [123, 124, 125, 125, 126, 126]
}
df_result_final = pd.DataFrame(data)

# Logic to process the dataframe

# Get the count of unique HLQ-EIMID combinations
count_df = df_result_final.groupby(['HLQ', 'EIMID']).size().reset_index(name='Count')

# Filter count dataframe where count is equal to 1 and sort by HLQ
new_dataframe = count_df[count_df['Count'] == 1].sort_values(by='HLQ')

# Get the EIMIDs for HLQs that have a count of 1
unique_eimids = new_dataframe.loc[new_dataframe.duplicated(subset='EIMID', keep=False), 'EIMID'].unique()

# Filter the original dataframe based on unique EIMIDs and HLQ
df_result_final = df_result_final[df_result_final['EIMID'].isin(unique_eimids) | ~df_result_final['HLQ'].isin(new_dataframe['HLQ'])]

# Print the result
print(df_result_final)
