import streamlit as st

from executive_dashboard import executive_page
from audience_dashboard import audience_page
from sql_page import sql_explorer
from ai_assistant import ai_page
from tableau_embed import tableau_page

st.set_page_config(layout="wide")

st.sidebar.title("Podcast BI Platform")

page=st.sidebar.radio(

"Navigation",

[
"Executive Dashboard",
"Audience Insights",
"SQL Explorer",
"Tableau Dashboard",
"AI Assistant"

]

)

if page=="Executive Dashboard":

    executive_page()

elif page=="Audience Insights":

    audience_page()

elif page=="SQL Explorer":

    sql_explorer()

elif page=="Tableau Dashboard":

    tableau_page()

elif page=="AI Assistant":

    ai_page()
