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

# ---------------- TREND ANALYSIS ----------------

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

    title="Listening Trend"

    )

    st.plotly_chart(fig,use_container_width=True)

# Detect Drop

    trend["change"]=trend.minutes.diff()

    drop_month=trend.loc[

    trend.change.idxmin()

    ]

# ---------------- DIAGNOSTIC ----------------

    st.header("Diagnostic Analysis")

    st.write(

    f"Performance dropped most during {drop_month.month}"

    )

# Category

    category_query="""

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

    cat=run_query(category_query)

    fig2=px.bar(

    cat,

    x="category",

    y="minutes",

    title="Category Engagement"

    )

    st.plotly_chart(fig2,use_container_width=True)

# Geography

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

    fig3=px.bar(

    geo,

    x="country",

    y="minutes",

    title="Country Engagement"

    )

    st.plotly_chart(fig3,use_container_width=True)

# Root Cause

    worst_country=geo.sort_values(

    "minutes"

    ).iloc[0]

    worst_category=cat.sort_values(

    "minutes"

    ).iloc[0]

    st.error(

f"""Root Cause:

Low engagement from {worst_country.country}
and declining {worst_category.category} podcasts.

"""

)

# Recommendation

    st.success(

f"""

Recommendation:

Increase promotion in {worst_country.country}.
Invest in improving {worst_category.category} content.

"""

)
