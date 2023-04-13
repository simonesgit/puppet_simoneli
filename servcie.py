# Rename the columns to avoid any conflicts with SQL keywords
df_em = df_em.rename(columns={'USER_NOTE': 'user_note'})
df_tpam = df_tpam.rename(columns={'TicketNbr': 'ticket_nbr'})

# Define a custom function to check if the ticket_nbr is a substring of the user_note
def contains_ticket_nbr(user_note, ticket_nbr):
    return ticket_nbr in user_note if user_note and ticket_nbr else False

# Register the custom function with pandasql
psql.register_function(contains_ticket_nbr, 'contains_ticket_nbr')

# SQL query to merge the DataFrames using the custom function
query = """
SELECT a.*, b.*
FROM df_em a
LEFT JOIN df_tpam b
ON contains_ticket_nbr(a.user_note, b.ticket_nbr)
"""

result_df = psql.sqldf(query, locals())
