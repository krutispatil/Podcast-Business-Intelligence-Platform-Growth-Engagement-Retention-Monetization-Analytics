import streamlit as st
from database import run_query
import plotly.express as px
import pandas as pd

def executive_page():

    st.title("Podcast Executive Command Center")

# ================= GLOBAL FILTERS =================

    countries=run_query(

    "SELECT DISTINCT country FROM listeners"

    )

    selected_country=st.sidebar.selectbox(

    "Country Filter",

    ["All"]+countries.country.tolist()

    )

    country_filter=""

    if selected_country!="All":

        country_filter=f"""

JOIN listeners l
ON s.listener_id=l.listener_id

WHERE l.country='{selected_country}'

"""

# ================= KPI SECTION =================

    kpi_query=f"""

SELECT

COUNT(DISTINCT s.listener_id) listeners,

SUM(s.listen_minutes) minutes,

AVG(s.completion_percent) completion

FROM sessions s

{country_filter}

"""

    kpis=run_query(kpi_query)

    col1,col2,col3=st.columns(3)

    col1.metric(

    "Active Listeners",

    int(kpis.listeners.iloc[0])

    )

    col2.metric(

    "Listening Minutes",

    int(kpis.minutes.iloc[0])

    )

    col3.metric(

    "Avg Completion",

    round(kpis.completion.iloc[0],2)

    )

# -------- Revenue KPI --------

    revenue_query="""

SELECT SUM(revenue_generated) revenue

FROM revenue

"""

    revenue=run_query(revenue_query)

    st.metric(

    "Total Revenue",

    int(revenue.revenue.iloc[0])

    )

    st.divider()

# ================= TREND =================

    trend_query=f"""

SELECT

strftime('%Y-%m',listen_start_time) month,

SUM(listen_minutes) minutes

FROM sessions s

{country_filter}

GROUP BY month

ORDER BY month

"""

    trend=run_query(trend_query)

    st.plotly_chart(

    px.line(

    trend,

    x="month",

    y="minutes",

    title="Listening Trend"

    ),

    use_container_width=True

    )

    trend["change"]=trend.minutes.diff()

    drop_month=trend.loc[trend.change.idxmin()].month

# ================= CATEGORY DRILLDOWN =================

    st.header("Category Analysis")

    cat_query="""

SELECT

p.category,
SUM(s.listen_minutes) minutes

FROM sessions s
JOIN episodes e

ON s.episode_id=e.episode_id

JOIN podcasts p

ON e.podcast_id=p.podcast_id

GROUP BY p.category

"""

    cat=run_query(cat_query)

    selected_category=st.selectbox(

"Drilldown Category",

cat.category.tolist()

)

    st.plotly_chart(

    px.bar(cat,x="category",y="minutes"),

    use_container_width=True

    )

# ================= COUNTRY =================

    geo_query="""

SELECT

l.country,
SUM(s.listen_minutes) minutes

FROM sessions s
JOIN listeners l

ON s.listener_id=l.listener_id

GROUP BY l.country

"""

    geo=run_query(geo_query)

    st.plotly_chart(

    px.bar(

    geo,

    x="country",

    y="minutes",

    title="Country Engagement"

    ),

    use_container_width=True

    )

# ================= ROOT CAUSE =================

    worst_country=geo.sort_values(

    "minutes"

    ).iloc[0]

    worst_category=cat.sort_values(

    "minutes"

    ).iloc[0]

# ================= STORY =================

    st.header("Executive Narrative")

    story=f"""

Performance decline observed in {drop_month}.

Primary Drivers:

Low engagement from {worst_country.country}.

Decline in {worst_category.category} category.

Recommendations:

Increase targeted marketing.

Introduce expert guest episodes.

Experiment shorter formats.

"""

    st.info(story)

# ================= BUSINESS QUESTIONS =================

    st.header("Executive Questions")

    questions={

"Top Revenue Category":

"""

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

"Premium Users":

"""

SELECT subscription_type,
COUNT(*)

FROM listeners

GROUP BY subscription_type

"""

}

    for q,sql in questions.items():

        st.subheader(q)

        st.dataframe(run_query(sql))
