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

# Step 4: Merge stories_df to get story counts per epic
story_counts = stories_df['S_EpicLink'].value_counts().reset_index()
story_counts.columns = ['E_key', 'activeStories']
overview_df = overview_df.merge(story_counts, how='left', on='E_key')

# Step 5: Calculate the number of 'In Progress' stories per epic
wip_story_counts = stories_df[stories_df['S_status'] == 'In Progress']['S_EpicLink'].value_counts().reset_index()
wip_story_counts.columns = ['E_key', 'wipStories']
overview_df = overview_df.merge(wip_story_counts, how='left', on='E_key')

# Step 6: Save the overview dataframe to a CSV file
overview_df.to_csv('export_overview_initiatives-epics.csv', index=False)
