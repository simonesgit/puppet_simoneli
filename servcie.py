import pandasql as psql

# Assuming you have two DataFrames: df_em and df_tpam

# Rename the columns to avoid any conflicts with SQL keywords
df_em = df_em.rename(columns={'USER_NOTE': 'user_note'})
df_tpam = df_tpam.rename(columns={'TicketNbr': 'ticket_nbr'})

# SQL query to merge the DataFrames
query = """
SELECT a.*, b.*
FROM df_em a
LEFT JOIN df_tpam b
ON a.user_note LIKE '%' || b.ticket_nbr || '%'
"""

result_df = psql.sqldf(query, locals())

print(result_df)
