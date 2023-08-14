import pandas as pd

# Create the original dataframe
data = {
    'HLQ': ['AAA', 'AAA', 'AAA', 'BBB', 'CCC', 'DDD'],
    'EIMID': [123, 124, 125, 125, 126, 126]
}
df_result_final = pd.DataFrame(data)

# Logic to process the dataframe

# Get the rows with 1 HLQ to multiple EIMID relationship
multiple_eimid = df_result_final.groupby('HLQ')['EIMID'].nunique().reset_index(name='Count')
rows_multiple_eimid = df_result_final[df_result_final['HLQ'].isin(multiple_eimid[multiple_eimid['Count'] > 1]['HLQ'])]

# Get the rows with 1 HLQ and 1 EIMID relationship
single_eimid = df_result_final.groupby('HLQ')['EIMID'].nunique().reset_index(name='Count')
rows_single_eimid = df_result_final[df_result_final['HLQ'].isin(single_eimid[single_eimid['Count'] == 1]['HLQ'])]

# Remove rows from rows_multiple_eimid if EIMID is in rows_single_eimid
rows_multiple_eimid = rows_multiple_eimid[~rows_multiple_eimid['EIMID'].isin(rows_single_eimid['EIMID'])]

# Combine rows_single_eimid and rows_multiple_eimid
result = pd.concat([rows_single_eimid, rows_multiple_eimid], ignore_index=True)

# Print the result
print(result)
