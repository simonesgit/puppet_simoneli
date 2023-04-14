import pandas as pd

# Dummy data for demonstration
df_em = pd.DataFrame({"Username": ["user1", "user2", "user3"], "USER_NOTE": ["TicketNbr: 123", "TicketNbr: 456", "TicketNbr: 789"]})
df_tpam = pd.DataFrame({"AccountName": ["user1", "user2", "user3"], "TicketNbr": ["123", "456", "789"], "Data": ["A", "B", "C"]})

def find_tpam_row(user_note, username, df_tpam):
    for _, row in df_tpam.iterrows():
        if row["TicketNbr"] in user_note and row["AccountName"] == username:
            return row
    return pd.Series()  # Return an empty Series if no match is found

matched_tpam = df_em.apply(lambda row: find_tpam_row(row["USER_NOTE"], row["Username"], df_tpam), axis=1)

# Concatenate the resulting DataFrames
df_result = pd.concat([df_em, matched_tpam.reset_index(drop=True)], axis=1)

print(df_result)
