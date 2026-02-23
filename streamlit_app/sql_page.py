import streamlit as st
from database import run_query

def sql_explorer():

    st.title("SQL Explorer")

    st.subheader("Database Schema")

    schema={

"podcasts":[

"podcast_id",
"podcast_name",
"category",
"language"

],

"episodes":[

"episode_id",
"podcast_id",
"duration_minutes"

],

"sessions":[

"session_id",
"listener_id",
"episode_id",
"listen_minutes",
"completion_percent",
"platform"

],

"revenue":[

"episode_id",
"revenue_generated"

]

}

    for table,cols in schema.items():

        st.write(f"### {table}")

        st.write(", ".join(cols))

    st.divider()

    query=st.text_area(

"Write SQL Query"

)

    if st.button("Run"):

        try:

            df=run_query(query)

            st.dataframe(df)

        except Exception as e:

            st.error(e)
