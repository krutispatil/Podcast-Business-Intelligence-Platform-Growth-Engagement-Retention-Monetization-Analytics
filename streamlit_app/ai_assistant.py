import streamlit as st
from database import run_query

BUSINESS_QUERIES={

"top revenue category":"""

SELECT p.category,
SUM(r.revenue_generated) revenue

FROM revenue r
JOIN episodes e
ON r.episode_id=e.episode_id
JOIN podcasts p
ON e.podcast_id=p.podcast_id

GROUP BY p.category
ORDER BY revenue DESC
LIMIT 1

""",

"platform usage":"""

SELECT platform,
COUNT(*) listens

FROM sessions

GROUP BY platform

""",

"listener count":"""

SELECT COUNT(DISTINCT listener_id)
AS listeners

FROM sessions

"""

}

def ai_page():

    st.title("AI Strategy Assistant")

    st.write(

    "Ask Business Questions."

    )

    q=st.text_input(

    "Example: top revenue category"

    )

    if q:

        q=q.lower()

        for key in BUSINESS_QUERIES:

            if key in q:

                df=run_query(

                BUSINESS_QUERIES[key]

                )

                st.dataframe(df)

                return

        st.warning(

        "Try: top revenue category / platform usage / listener count"

        )
