import streamlit as st

from executive_dashboard import executive_page
from data_storytelling import data_storytelling_page
from audience_dashboard import audience_page
from sql_page import sql_explorer

st.set_page_config(layout="wide")

st.sidebar.title("Podcast BI Platform")

page=st.sidebar.radio(

"Navigation",

[
"Executive Dashboard",
"Data Storytelling",
"Audience Insights",
"SQL Explorer"

]

)

if page=="Executive Dashboard":

    executive_page()

elif page=="Data Storytelling":

    data_storytelling_page()

elif page=="Audience Insights":

    audience_page()

elif page=="SQL Explorer":

    sql_explorer()
