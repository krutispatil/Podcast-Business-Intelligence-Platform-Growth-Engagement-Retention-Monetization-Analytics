import streamlit as st

def tableau_page():

    st.title("Tableau Dashboard")

    st.components.v1.iframe(

"https://public.tableau.com/views/YOURDASHBOARD",

height=900

)
