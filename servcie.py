def find_tpam_row(user_note, username, df_tpam):
    for idx, tpam_row in df_tpam.iterrows():
        if contains_ticket_nbr(user_note, tpam_row["TicketNbr"]) and tpam_row["AccountName"] == username:
            return idx
    return None

  
matched_indices = set()
matched_tpam = df_em.apply(lambda x: find_tpam_row(x["USER_NOTE"], x["Username"], df_tpam), axis=1)

# Add matched rows to matched_tpam DataFrame
matched_rows = [df_tpam.loc[idx] for idx in matched_tpam if idx is not None]
matched_indices.update(matched_tpam.dropna().astype(int))

# Create an empty DataFrame for unmatched rows
unmatched_tpam = pd.DataFrame(columns=df_tpam.columns)

# Add unmatched rows to unmatched_tpam DataFrame
unmatched_rows = [row for idx, row in df_tpam.iterrows() if idx not in matched_indices]
unmatched_tpam = pd.concat([unmatched_tpam, pd.DataFrame(unmatched_rows)], ignore_index=True)


# Merge df_em and matched_tpam
df_result = pd.concat([df_em, pd.DataFrame(matched_rows).reset_index(drop=True)], axis=1)

# Add unmatched_tpam to the final result
df_result = pd.concat([df_result, unmatched_tpam], ignore_index=True)
