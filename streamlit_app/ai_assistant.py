import streamlit as st
from database import run_query

def ai_page():

    st.title("AI Strategy Assistant")

    st.write(

"Ask questions like:\n"
"Which country performs worst?\n"
"Top revenue category?"

)

    question=st.text_input("Ask")

    if question:

        question=question.lower()

        if "country" in question:

            sql="""

SELECT country,
COUNT(*) listens

FROM listeners l
JOIN sessions s

ON l.listener_id=s.listener_id

GROUP BY country
ORDER BY listens DESC

"""

        elif "revenue" in question:

            sql=open(

"sql_queries/revenue_by_category.sql"

).read()

        elif "platform" in question:

            sql="""

SELECT platform,
COUNT(*) listens

FROM sessions

GROUP BY platform

"""

        else:

            st.warning("Try another business question")

            return

        df=run_query(sql)

        st.dataframe(df)
