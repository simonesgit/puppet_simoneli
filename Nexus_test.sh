import pandas as pd

def filter_tpam_by_em_notes(df_em, df_tpam):
    matched_rows = []

    for _, em_row in df_em.iterrows():
        user_note = em_row['USER_NOTE']
        username = em_row['Username']
        matched_tpam_rows = df_tpam[(df_tpam['TicketNbr'].apply(lambda x: str(x) in user_note)) &
                                     (df_tpam['AccountName'] == username)]

        if not matched_tpam_rows.empty:
            for _, tpam_row in matched_tpam_rows.iterrows():
                merged_row = em_row.copy()
                merged_row.update(tpam_row)
                matched_rows.append(merged_row.to_dict())

    matched_df = pd.DataFrame(matched_rows)
    return matched_df

# Assuming you already have df_em and df_tpam loaded
merged_df = filter_tpam_by_em_notes(df_em, df_tpam)
