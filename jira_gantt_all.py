import pandas as pd

# Step 1: Read contents from the three reports and store as dataframes
initiatives_df = pd.read_csv('export_all_initiatives.csv')
epics_df = pd.read_csv('export_all_epics.csv')
stories_df = pd.read_csv('export_all_stories.csv')

# Step 2: Rename column names with prefixes based on the source file
initiatives_df = initiatives_df.add_prefix('I_')
epics_df = epics_df.add_prefix('E_')
stories_df = stories_df.add_prefix('S_')

# Step 3: Update target end if due date is later or there's no target date
initiatives_df['I_TargetEnd'] = initiatives_df.apply(lambda row: row['I_EndDate'] if pd.notnull(row['I_EndDate']) else row['I_TargetEnd'], axis=1)
epics_df['E_TargetEnd'] = epics_df.apply(lambda row: row['E_duedate'] if pd.notnull(row['E_duedate']) else row['E_TargetEnd'], axis=1)

# Step 4: Create 'resource' column for each dataframe
initiatives_df['resource'] = ''
epics_df['resource'] = ''
stories_df['resource'] = ''

# Step 5: Assign resource value of stories
stories_df['resource'] = stories_df.apply(lambda row: [row['S_assignee'], row['S_AdditionalAssignee']], axis=1)
stories_df['resource'] = stories_df['resource'].apply(lambda x: ', '.join(list(set(filter(None, map(str, x))))))  # Convert values to strings, remove duplicates, and generate resource string

# Step 6: Assign resource value of epics
unique_epic_ids = epics_df['E_key'].unique()
for epic_id in unique_epic_ids:
    epic_row = epics_df[epics_df['E_key'] == epic_id].iloc[0]
    epic_stories = stories_df[stories_df['S_EpicLink'] == epic_id]
    epic_resource = [epic_row['E_assignee'], epic_row['E_AdditionalAssignee']] + list(epic_stories['resource'])
    epic_resource = ', '.join(list(set(filter(None, map(str, epic_resource))))  # Convert values to strings, remove duplicates, and generate resource string
    epics_df.loc[epics_df['E_key'] == epic_id, 'resource'] = epic_resource

# Step 7: Assign resource value of initiatives
unique_initiative_ids = initiatives_df['I_key'].unique()
for initiative_id in unique_initiative_ids:
    initiative_row = initiatives_df[initiatives_df['I_key'] == initiative_id].iloc[0]
    initiative_epics = epics_df[epics_df['E_PartentLink'] == initiative_id]
    initiative_resource = [initiative_row['I_assignee'], initiative_row['I_AdditionalAssignee']] + list(initiative_epics['resource'])
    initiative_resource = ', '.join(list(set(filter(None, map(str, initiative_resource))))  # Convert values to strings, remove duplicates, and generate resource string
    initiatives_df.loc[initiatives_df['I_key'] == initiative_id, 'resource'] = initiative_resource
