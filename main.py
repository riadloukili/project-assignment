import streamlit as st
from streamlit.uploaded_file_manager import UploadedFile
import pandas as pd
import io

from assigner import assign

if 'results' not in st.session_state:
  st.session_state.results = None

st.set_page_config(page_title="Project Assignment", page_icon="🤖")
st.markdown(r"<style>footer, header button { visibility: hidden }</style>", unsafe_allow_html=True)

st.title("Project Assignment")
st.header("How does it work?")
st.write("The way the algorithm works is that it tries to give all group their first choices. If multiple groups choose a project as their first choice, it's going to assign it randomly to a group (or groups). After assigning the first choices, it moves to the second choice and tries to give all groups their second choice. If multiple people have a group as their second choice it assigns it to random group(s). And so on...")

st.header("Instructions")
st.write("You can get started by uploading an Excel file in the format described below.")

example_df = pd.DataFrame(
  data=[
    [2, 3, 1],
    [2, 3, 1],
    [3, 1, 2]
  ],
  columns=['projet 1', 'projet 2', 'projet 3'],
  index=["group 1", "group 2", "group 3"]
)
st.write("The Excel should have the following format with columns representing the projects and the rows representing the groups and their choices in order.")
st.table(example_df)
st.caption('In the example above, groupe 1 has "project 3" as their first choice, "project 1" as their second choice, and finally "project 2" as their third choice.')
st.write("You can download the example excel using the following link.")
@st.cache
def convert_df(df: pd.DataFrame):
  memory_file = io.BytesIO()
  df_copy = df.copy()
  df_copy.to_excel(memory_file, encoding='utf-8')
  memory_file.seek(0)
  return memory_file.getvalue()

st.download_button(
  label="Download Example (.xlsx)",
  data=convert_df(example_df),
  file_name='example.xlsx',
  mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.header("Upload data")
st.write("Once you fill in the Excel file in the format described in the **Instructions** section, you can upload it here and proceed to the next step.")
uploaded_file: UploadedFile = st.file_uploader(
  label="Choices Excel File",
  type="xlsx"
)
if uploaded_file is not None:
  df: pd.DataFrame = pd.read_excel(uploaded_file, index_col=0)
  st.success("Data loaded sucessfully, here's a quick overview of what we got.")
  st.header("Overview")
  st.subheader("Preview")
  st.dataframe(df.style.highlight_min(axis=1, color="#8e44ad"))
  col1, col2 = st.columns(2)
  with col1:
    st.metric(label="Number of projects", value="%d" % len(df.columns))
  with col2:
    st.metric(label="Number of groups", value="%d" % len(df.index))

  st.header("Assignment")
  st.subheader("Settings")
  groups_per_project = st.slider('Max # of groups per project', min_value=1, max_value=len(df.index))
  st.metric(label="# of groups left out", value="%d" % max(0, len(df.index) - len(df.columns) * groups_per_project))

  def assign_projects():
    st.session_state.results = assign(df, groups_per_project)

  st.button("Assign projects", on_click=assign_projects)
  
  if st.session_state.results is not None:
    st.subheader("Results")
    st.success("Success! Here's the final groups-projects assignment.")
    mapping = st.session_state.results
    assigned_df = pd.DataFrame(data=[], index=df.index, columns=["Project", "Choice"])
    for project, groups in mapping.items():
      for group, choice in groups:
        assigned_df.loc[group, :] = [project, choice]
    st.table(assigned_df.style.highlight_null(null_color="#c0392b"))
    st.download_button(
      label="Download Result (.xlsx)",
      data=convert_df(assigned_df),
      file_name='result.xlsx',
      mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      on_click=lambda: st.balloons()
    )
    
st.markdown("""<div style="margin: 32px auto 16px;width: 128px;height: 128px;background: url(https://java.riadloukili.com/img/club_logo.png) no-repeat center;background-size: contain;"></div>""", unsafe_allow_html=True)

