import pandas as pd

# Create a sample dataframe
data = {'TP_Reason': ["**PARDS**-Category: . Activity: Investigation. Detail: PA Task No:PAM456789, Child Task No:, Access Type:Read-Write, Summary for Request: To Access CCM."]}
df = pd.DataFrame(data)

# Define the regular expression patterns for each new column
category_pattern = r"Category:\s*(.*?)[. ]"
activity_pattern = r"Activity:\s*(.*?)[. ]"
pa_task_no_pattern = r"PA Task No:\s*(.*?)[, ]"
child_task_no_pattern = r"Child Task No:\s*(.*?)[, ]"
access_type_pattern = r"Access Type:\s*(.*?)[, ]"
summary_pattern = r"Summary for Request:\s*(.*)"

# Use str.extract to create new columns from the TP_Reason column
df['TP_Category'] = df['TP_Reason'].str.extract(category_pattern)
df['TP_Activity'] = df['TP_Reason'].str.extract(activity_pattern)
df['TP_PATaskNo'] = df['TP_Reason'].str.extract(pa_task_no_pattern)
df['TP_ChildTaskNo'] = df['TP_Reason'].str.extract(child_task_no_pattern)
df['TP_AccessType'] = df['TP_Reason'].str.extract(access_type_pattern)
df['TP_Summary'] = df['TP_Reason'].str.extract(summary_pattern)

print(df)


