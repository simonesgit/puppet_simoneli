import pandas as pd

def special_processing(df):
    tmp_su, tmp_un, tmp_hn = None, None, None

    for index, row in df.iterrows():
        if row['Operation'] == 'LOGIN USER':
            tmp_su = row['System_Username']
            tmp_un = row['Username']
            tmp_hn = row['HOSTNAME']

            # Query rows after the current row
            for inner_index, inner_row in df.iloc[index+1:].iterrows():
                if (inner_row['Username'] == tmp_un and
                    inner_row['HOSTNAME'] == tmp_hn and
                    (inner_row['System_Username'] == '' or pd.isna(inner_row['System_Username']))):
                    # Set System_Username to the temporary stored value
                    df.at[inner_index, 'System_Username'] = tmp_su

# Sample data for testing
data = {
    'Operation': ['LOGIN USER', 'QUERY', 'LOGIN USER', 'QUERY'],
    'System_Username': ['sys_user1', None, 'sys_user2', None],
    'Username': ['user1', 'user1', 'user2', 'user2'],
    'HOSTNAME': ['host1', 'host1', 'host2', 'host2']
}

df = pd.DataFrame(data)

# Fill missing values with empty strings
df.fillna('', inplace=True)

print("Before processing:")
print(df)

special_processing(df)

print("\nAfter processing:")
print(df)
