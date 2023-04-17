def find_tpam_row(user_note, username, df_tpam):
    ticket_nbr = extract_ticket_nbr(user_note)
    
    if ticket_nbr:
        matched_rows = df_tpam[(df_tpam["TicketNbr"] == ticket_nbr) & (df_tpam["AccountName"] == username)]
        
        if not matched_rows.empty:
            return matched_rows.iloc[0]

    return pd.Series(dtype="object")
