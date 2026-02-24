import streamlit as st
from database import run_query
import plotly.express as px

def executive_page():

    st.title("Executive Podcast Intelligence")

# ---------------- KPI HEALTH ----------------

    kpi_query="""

SELECT

COUNT(DISTINCT listener_id) listeners,
SUM(listen_minutes) minutes

FROM sessions;

"""

    kpis=run_query(kpi_query)

    col1,col2=st.columns(2)

    col1.metric(

    "Active Listeners",

    int(kpis.listeners.iloc[0])

    )

    col2.metric(

    "Listening Minutes",

    int(kpis.minutes.iloc[0])

    )

    st.divider()

# ---------------- TREND ----------------

    trend_query="""

SELECT

strftime('%Y-%m',listen_start_time) month,

SUM(listen_minutes) minutes

FROM sessions

GROUP BY month
ORDER BY month

"""

    trend=run_query(trend_query)

    fig=px.line(

    trend,

    x="month",

    y="minutes",

    title="Monthly Engagement Trend"

    )

    st.plotly_chart(fig,use_container_width=True)

    trend["change"]=trend.minutes.diff()

    drop_month=trend.loc[trend.change.idxmin()].month

# ---------------- CATEGORY ----------------

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

    st.plotly_chart(

    px.bar(

    cat,

    x="category",

    y="minutes",

    title="Category Engagement"

    ),

    use_container_width=True

    )

# ---------------- COUNTRY ----------------

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

# ---------------- ROOT CAUSE ----------------

    worst_country=geo.sort_values(

    "minutes"

    ).iloc[0]

    worst_category=cat.sort_values(

    "minutes"

    ).iloc[0]

# ---------------- EXECUTIVE SUMMARY ----------------

    st.header("Executive Summary")

    st.error(

f"""

Performance decline detected in {drop_month}.

Root Cause:

Lowest engagement from {worst_country.country}.

Decline in {worst_category.category} podcast performance.

"""

)

    st.success(

f"""

Recommended Actions:

Increase localized marketing in {worst_country.country}.

Invest in improving {worst_category.category} podcast quality.

Experiment with shorter episode formats.

"""

)

# ---------------- BUSINESS QUESTIONS ----------------

    st.header("Executive Business Questions")

# Revenue Category

    revenue_query="""

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

"""

    st.subheader(

"Which Category Drives Revenue?"

)

    st.dataframe(

    run_query(revenue_query)

    )

# Platform

    platform_query="""

SELECT platform,
COUNT(*) listens

FROM sessions

GROUP BY platform
ORDER BY listens DESC

"""

    st.subheader(

"Most Used Platform?"

)

    st.dataframe(

    run_query(platform_query)

    )
