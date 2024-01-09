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

# Step 5: Calculate the number of 'In Progress' and 'Completed' stories per epic
in_progress_completed_story_counts = stories_df[stories_df['S_status'].isin(['In Progress', 'Completed'])]['S_EpicLink'].value_counts().reset_index()
in_progress_completed_story_counts.columns = ['E_key', 'wipStories']
overview_df = overview_df.merge(in_progress_completed_story_counts, how='left', on='E_key')

# Step 6: Reorganize the column sequence
column_sequence = ['I_key', 'I_assignee', 'I_AdditionalAssignee', 'I_summary', 'I_priority', 'I_status', 'I_labels', 'I_duedate','I_TargetStart', 'I_TargetEnd',
                   'E_key', 'E_assignee', 'E_AdditionalAssignee', 'E_summary', 'E_priority', 'E_status', 'E_labels', 'E_ParentLink',
                   'E_ResolutionNote', 'E_created', 'E_EpicName', 'E_description', 'E_resolution', 'E_progress', 'E_duedate',
                   'E_TargetStart', 'E_TargetEnd', 'E_StartDate', 'E_EndDate', 'E_duedate',
                   'activeStories', 'wipStories']
overview_df = overview_df[column_sequence]

# Step 7: Update I_TargetStart and I_TargetEnd based on E_TargetStart and E_TargetEnd
warn_message = "Value updated: "
for index, row in overview_df.iterrows():
    i_target_start = row['I_TargetStart']
    e_target_start = row['E_TargetStart']
    if pd.notnull(e_target_start) and (pd.isnull(i_target_start) or e_target_start < i_target_start):
        overview_df.at[index, 'I_TargetStart'] = e_target_start
        warn_message += f"I_Key: {row['I_key']}, E_TargetStart: {e_target_start}, "
    
    i_target_end = row['I_TargetEnd']
    e_target_end = row['E_TargetEnd']
    if pd.notnull(e_target_end) and (pd.isnull(i_target_end) or e_target_end > i_target_end):
        overview_df.at[index, 'I_TargetEnd'] = e_target_end
        warn_message += f"I_Key: {row['I_key']}, E_TargetEnd: {e_target_end}, "
        
    i_due_date = row['I_duedate']
    if pd.notnull(i_due_date) and (pd.isnull(i_target_end) or i_due_date > i_target_end):
        overview_df.at[index, 'I_TargetEnd'] = i_due_date
        warn_message += f"I_Key: {row['I_key']}, I_duedate: {i_due_date}, "
    
    e_due_date = row['E_duedate']
    if pd.notnull(e_due_date) and (pd.isnull(e_target_end) or e_due_date > e_target_end):
        overview_df.at[index, 'E_TargetEnd'] = e_due_date
        warn_message += f"I_Key: {row['I_key']}, E_duedate: {e_due_date}, "
        
if warn_message != "Value updated: ":
    print(warn_message[:-2])  # Print warning message if any values were updated

# Step 8: Create the gantt dataframe
df_gantt = pd.DataFrame(columns=['I_key', 'objective_key', 'objective', 'TargetStart', 'TargetEnd'])

# Step 9: Add rows to the gantt dataframe
for index, row in overview_df.iterrows():
    df_gantt = df_gantt.append({'I_key': row['I_key'], 'objective_key': row['I_key'], 'objective': row['I_summary'],
                                'TargetStart': row['I_TargetStart'], 'TargetEnd': row['I_TargetEnd']}, ignore_index=True)
    df_gantt = df_gantt.append({'I_key': row['I_key'], 'objective_key': row['E_key'], 'objective': row['E_summary'],
                                'TargetStart': row['E_TargetStart'], 'TargetEnd': row['E_TargetEnd']}, ignore_index=True)

# Step 10: Save the gantt dataframe to a CSV file
df_gantt.to_csv('export_gantt_initiative-epics.csv', index=False)
