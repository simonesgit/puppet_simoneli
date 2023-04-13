def find_tpamlogs_row(user_note, tpamlogs, pattern=r'in\d+'):
    match = re.search(pattern, user_note)
    if match:
        ticket_nbr = match.group(0)
        tpamlogs_row = tpamlogs[tpamlogs['TicketNbr'] == ticket_nbr]
        if not tpamlogs_row.empty:
            return tpamlogs_row.iloc[0]
    return None

# Apply the function to the USER_NOTE column to create a new DataFrame with matched rows from tpamlogs
matched_tpamlogs = emlogs['USER_NOTE'].apply(find_tpamlogs_row, args=(tpamlogs,))

# Combine the matched rows with the original tpamlogs DataFrame
matched_tpamlogs = pd.concat([matched_tpamlogs.dropna().reset_index(drop=True), tpamlogs]).drop_duplicates(keep=False).reset_index(drop=True)

# Now concatenate emlogs and matched_tpamlogs
result_df = pd.concat([emlogs, matched_tpamlogs], axis=1)
