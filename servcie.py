# Define a custom function to find the corresponding row in df_tpam based on TicketNbr
def find_tpamlogs_row(user_note, tpamlogs):
    for idx, row in tpamlogs.iterrows():
        if row['TicketNbr'] in user_note:
            return row
    return pd.Series(index=tpamlogs.columns)

# Apply the function to the USER_NOTE column to create a new DataFrame with matched rows from df_tpam
matched_tpam = df_em['USER_NOTE'].apply(find_tpamlogs_row, args=(df_tpam,))

# Now concatenate df_em and matched_tpam
result_df = pd.concat([df_em, matched_tpam.reset_index(drop=True)], axis=1)
