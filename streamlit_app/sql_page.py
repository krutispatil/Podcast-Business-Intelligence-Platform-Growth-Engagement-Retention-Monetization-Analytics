import streamlit as st
from database import run_query

def sql_explorer():

    st.title("SQL Explorer")

    query=st.text_area(

"Write SQL Query"

)

    if st.button("Run"):

        try:

            df=run_query(query)

            st.dataframe(df)

        except Exception as e:

            st.error(e)
