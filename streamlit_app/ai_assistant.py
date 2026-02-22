import streamlit as st
from database import run_query

def ai_page():

    st.title("AI Analytics Assistant")

    question=st.text_input(

"Ask Business Question"

)

    if question:

        if "revenue" in question.lower():

            query="""

SELECT SUM(revenue_generated)

FROM revenue

"""

        elif "platform" in question.lower():

            query="""

SELECT platform,COUNT(*) listens

FROM sessions

GROUP BY platform

"""

        else:

            st.write("Try asking about revenue or platform usage")

            return

        df=run_query(query)

        st.dataframe(df)
