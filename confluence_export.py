import adodbapi

def generate_report():
    # Establish a connection to the database
    db_connection = adodbapi.connect('<your_db_connection_string>')

    # Define the list of AD groups
    ad_groups = ['group1', 'group2', 'group3']  # Update with your actual AD group names

    # Execute the query for each AD group and generate the report
    for ad_group in ad_groups:
        query = f"SELECT cn, mail FROM <db_connection> WHERE groupMembership = '{ad_group}'"
        cursor = db_connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()

        if results:
            print(f"AD Group: {ad_group}")
            for result in results:
                username = result[0]
                email = result[1]
                print(f"CN: {username}, Email: {email}")
        else:
            print(f"No results found for AD Group: {ad_group}")

    # Close the database connection
    db_connection.close()

# Call the function to generate the report
generate_report()
