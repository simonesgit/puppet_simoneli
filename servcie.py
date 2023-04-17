# Create an empty DataFrame with the same columns as df_em and the same number of rows as unmatched_tpam
empty_df_em = pd.DataFrame(np.nan, index=range(len(unmatched_tpam)), columns=df_em.columns)

# Concatenate empty_df_em with unmatched_tpam
unmatched_combined = pd.concat([empty_df_em.reset_index(drop=True), unmatched_tpam.reset_index(drop=True)], axis=1)

# Concatenate df_result with unmatched_combined
df_result = pd.concat([df_result, unmatched_combined], ignore_index=True)
