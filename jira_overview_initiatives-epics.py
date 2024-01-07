import pandas as pd

# Step 1: Read contents from the three reports and store as dataframes
initiatives_df = pd.read_csv('export_all_initiatives.csv')
epics_df = pd.read_csv('export_all_epics.csv')
stories_df = pd.read_csv('export_all_stories.csv')

# Step 2: Rename column names with prefixes based on the source file
initiatives_df = initiatives_df.add_prefix('I_')
epics_df = epics_df.add_prefix('E_')
stories_df = stories_df.add_prefix('S_')

# Step 3: Create a new dataframe to join initiatives and epics information
overview_df = epics_df.merge(initiatives_df, how='left', left_on='E_ParentLink', right_on='I_key')
overview_df['openStories'] = overview_df.groupby('E_key')['E_key'].transform('count')
overview_df['wipStories'] = overview_df.groupby('E_key')['E_status'].transform(lambda x: (x == 'In Progress').sum())

# Step 4: Save the overview dataframe to a CSV file
overview_df.to_csv('overview_initiatives-epics.csv', index=False)
