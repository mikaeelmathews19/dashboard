import streamlit as st
import pandas as pd

@st.cache_data
def load_data(file_path):
    return pd.read_excel(file_path)

file_path = ""
file_path1 = ""
file_path2 = ""

df = load_data(file_path)
removed_nulls_df = df[df['session_id'].notnull()]
df1 = load_data(file_path1)
df2 = load_data(file_path2)

# Sidebar title
st.sidebar.title("Select filters:")
bank = st.sidebar.multiselect(
    "Select bank:",
    options=df["bank"].unique(),
    default=df["bank"].unique()
)

is_error = st.sidebar.multiselect(
    "Select is_error:",
    options=df["is_error"].unique(),
    default=df["is_error"].unique()
)

df_selection = removed_nulls_df.query(
    "bank == @bank & is_error == @is_error"
)

# Check if the dataframe is empty:
if df_selection.empty:
    st.warning("No data available based on the current filter settings!")
    st.stop() # This will halt the app from further execution.

    # ---- MAINPAGE ----
st.title(":bar_chart: :money_with_wings: Dashboard App")
st.markdown("##")

st.divider()

# TOP KPI's
total_instructions = int(df1['instruction_id'].count())
total_sessions = int(df_selection['session_id'].count())
session_id_by_instruction_id = df_selection.groupby('instruction_id')['session_id'].count()
average_sessions_per_instruction = round(session_id_by_instruction_id.mean(),2)
session_id_with_error = df_selection[df_selection['is_error'] == 1]['session_id'].count()
error_rate = round((session_id_with_error / total_sessions) * 100,2)



column1, column2, column3, column4 = st.columns(4)
with column1:
    st.metric(label="Total Instructions:", value=total_instructions)
with column2:
    st.metric(label="Total Sessions:", value=total_sessions)
with column3:
    st.metric(label="Average Sessions per Instruction:", value=average_sessions_per_instruction)
with column4:
    st.metric(label="Error Rate:", value=f"{error_rate}%")


st.write("## % Instructions per Bank")
instruction_id_per_bank = df.groupby('bank')['instruction_id'].count()
total_instruction_ids = instruction_id_per_bank.sum()
proportion_instruction_id_per_bank = round((instruction_id_per_bank / total_instruction_ids) * 100, 2)
st.bar_chart(proportion_instruction_id_per_bank)


# Create a bar chart for session IDs count by bank
st.write("## Sessions per Bank")
session_id_by_bank = df_selection.groupby('bank')['session_id'].count()
st.bar_chart(session_id_by_bank)

# Create a bar chart for session IDs count by instruction ID
st.write("## Sessions per Instruction")
session_id_by_instruction_id = df_selection.groupby('instruction_id')['session_id'].count()
st.bar_chart(session_id_by_instruction_id)

st.write("## Error Rate per Bank")
session_id_with_error_by_bank = df_selection[df_selection['is_error'] == 1].groupby('bank')['session_id'].count()
proportion_with_error_by_bank = round((session_id_with_error_by_bank / session_id_by_bank) * 100,2)
st.bar_chart(proportion_with_error_by_bank)

st.write("## Overall Instruction Time")
removed_null_instructions = df_selection[df_selection['instruction_id'].notnull()]
removed_null_instructions['instruction_time'] = (pd.to_datetime(removed_null_instructions['updated_at']) - pd.to_datetime(removed_null_instructions['created_at'])).dt.total_seconds() / 60
instruction_time_df = removed_null_instructions.groupby(['instruction_id', 'bank']).agg({
    'instruction_time': 'sum'
}).reset_index()
instruction_time_df['instruction_id'] = instruction_time_df['instruction_id'].astype(int)
describe_instruction_time_df = instruction_time_df['instruction_time'].describe()

column5, column6 = st.columns(2)
with column5:
    st.dataframe(instruction_time_df)
with column6:
    st.dataframe(describe_instruction_time_df)

st.write("## Average Instruction Time per Bank")
avg_instruction_time_per_bank = instruction_time_df.groupby(['bank']).agg({
    'instruction_time': 'mean'
})
avg_instruction_time_per_bank['instruction_time'] = avg_instruction_time_per_bank['instruction_time'].round(2)
st.bar_chart(avg_instruction_time_per_bank)

st.write("## Errors by Instruction Type")
instruction_id_by_instruction_type = df2.groupby(['instruction_type']).agg({
    'instruction_id': 'count',
    'is_error': 'sum'
})

instruction_id_by_instruction_type['error_proportion'] = (instruction_id_by_instruction_type['is_error'] / instruction_id_by_instruction_type['instruction_id']) * 100
instruction_id_by_instruction_type['error_proportion'] = instruction_id_by_instruction_type['error_proportion'].round(2)

st.dataframe(instruction_id_by_instruction_type)

st.divider()

st.subheader('Insights & Recommendations')
