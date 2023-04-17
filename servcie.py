def special_processing(df):
    user_mapping = {}

    for index, row in df.iterrows():
        if row['Operation'] == 'LOGIN USER':
            key = (row['Username'], row['HOSTNAME'])
            user_mapping[key] = row['System_Username']

        elif row['Operation'] == 'LOGOUT USER':
            key = (row['Username'], row['HOSTNAME'])
            if key in user_mapping:
                del user_mapping[key]

        else:
            key = (row['Username'], row['HOSTNAME'])
            if key in user_mapping and (row['System_Username'] == '' or pd.isna(row['System_Username'])):
                df.at[index, 'System_Username'] = user_mapping[key]
