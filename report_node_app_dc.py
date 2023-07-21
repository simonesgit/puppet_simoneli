import cx_Oracle
import pandas as pd
import xlsxwriter

# Define the list of database connection information
database_list = [
    {
        'db_name': 'Database1',
        'username': 'user1',
        'password': 'password1',
        'hostname': 'hostname1',
        'port': 'port1',
        'service_name': 'service1'
    },
    {
        'db_name': 'Database2',
        'username': 'user2',
        'password': 'password2',
        'hostname': 'hostname2',
        'port': 'port2',
        'service_name': 'service2'
    },
    # Add more databases if needed
]

# Function to execute the query and return the dataframe
def execute_query(connection):
    query = '''
        SELECT dt.data_center, dt.sched_table, dj.table_id, dj.application, dj.node_id
        FROM def_ver_job dj
        JOIN def_ver_tables dt ON dj.table_id = dt.table_id
        WHERE dj.task_type = 'Job'
        ORDER BY dt.data_center, dt.sched_table
    '''
    cursor = connection.cursor()
    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=columns)
    return df

# Create a dictionary to store all the dataframes
df_all = pd.DataFrame()

# Iterate over the databases and execute the query for each one
for db_info in database_list:
    # Establish connection to the database
    dsn = cx_Oracle.makedsn(
        db_info['hostname'],
        db_info['port'],
        service_name=db_info['service_name']
    )
    connection = cx_Oracle.connect(
        db_info['username'],
        db_info['password'],
        dsn,
        encoding='UTF-8'
    )
    
    # Execute the query and store the result in a dataframe
    df_db = execute_query(connection)
    
    # Concatenate the dataframe to the df_all dataframe
    df_all = pd.concat([df_all, df_db])
    
    # Close the database connection
    connection.close()

# Create an Excel file using xlsxwriter
filename = 'TABLE_NODE.xlsx'
workbook = xlsxwriter.Workbook(filename)

# Create a worksheet for df_all and write its data to the sheet
worksheet_all = workbook.add_worksheet('All Data')
for col_num, column_name in enumerate(df_all.columns):
    max_width = len(column_name)
    for value in df_all[column_name]:
        max_width = max(max_width, len(str(value)))
    worksheet_all.set_column(col_num, col_num, max_width)
    worksheet_all.write(0, col_num, column_name)
for row_num, row_data in enumerate(df_all.values, start=1):
    for col_num, value in enumerate(row_data):
        worksheet_all.write(row_num, col_num, value)

# Create a worksheet for each individual dataframe and write their data to the sheets
for db_info in database_list:
    df_db = pd.DataFrame()
    # Extract the corresponding dataframe from df_all based on the database name
    df_db = df_all[df_all['db_name'] == db_info['db_name']]
    worksheet_db = workbook.add_worksheet(db_info['db_name'])
    for col_num, column_name in enumerate(df_db.columns):
        max_width = len(column_name)
        for value in df_db[column_name]:
            max_width = max(max_width, len(str(value)))
        worksheet_db.set_column(col_num, col_num, max_width)
        worksheet_db.write(0, col_num, column_name)
    for row_num, row_data in enumerate(df_db.values, start=1):
        for col_num, value in enumerate(row_data):
            worksheet_db.write(row_num, col_num, value)

# Close the workbook
workbook.close()

print(f"Data extraction complete. The extracted data has been saved to {filename}.")
