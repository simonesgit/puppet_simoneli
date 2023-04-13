def save_dataframe_as_excel_xlsxwriter(df, filename, sheet_name='Sheet1', max_width_columns=None):
    # Create a Pandas Excel writer using XlsxWriter as the engine
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')

    # Convert the DataFrame to an XlsxWriter Excel object
    df.to_excel(writer, sheet_name=sheet_name, index=False)

    # Get the xlsxwriter workbook and worksheet objects
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]

    # Adjust column widths
    for col_idx, col in enumerate(df.columns):
        if max_width_columns is None or col not in max_width_columns:
            max_data_length = df[col].astype(str).str.len().max()
            max_col_name_length = len(col)
            max_length = max(max_data_length, max_col_name_length)
            worksheet.set_column(col_idx, col_idx, max_length + 2)

    # Close the Pandas Excel writer and output the Excel file using the save method of the workbook object
    workbook.close()
