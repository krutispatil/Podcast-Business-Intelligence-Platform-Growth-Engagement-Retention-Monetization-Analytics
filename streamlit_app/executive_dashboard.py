import streamlit as st
from database import run_query
import plotly.express as px
import pandas as pd

def executive_page():

    st.title("Executive Intelligence Platform")

# ================= KPI HEALTH =================

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
    if st.button("Why Did Performance Change?"):
        st.write("Running Multi-Factor Analysis...")

# ================= TREND =================

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

# Detect worst month

    trend["change"]=trend.minutes.diff()

    drop_month=trend.loc[trend.change.idxmin()].month

    st.warning(

    f"Performance drop detected in {drop_month}"

    )

# ================= AUTO ROOT CAUSE =================

    st.header("AI Root Cause Diagnostics")

# Category

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

# Platform

    platform_query="""

SELECT

platform,
COUNT(*) listens

FROM sessions

GROUP BY platform

"""

    plat=run_query(platform_query)

# Visuals

    colA,colB=st.columns(2)

    colA.plotly_chart(

    px.bar(cat,x="category",y="minutes",
    title="Category Engagement"),

    use_container_width=True

    )

    colB.plotly_chart(

    px.bar(geo,x="country",y="minutes",
    title="Country Engagement"),

    use_container_width=True

    )

    st.plotly_chart(

    px.pie(

    plat,

    names="platform",

    values="listens",

    title="Platform Share"

    ),

    use_container_width=True

    )

# Root Cause Logic

    worst_country=geo.sort_values(

    "minutes"

    ).iloc[0]

    worst_category=cat.sort_values(

    "minutes"

    ).iloc[0]

# ================= STORY =================

    st.error(

f"""

Root Cause Summary:

Lowest engagement detected in {worst_country.country}.

Category decline observed in {worst_category.category} podcasts.

"""

)

# ================= ACTION =================

    st.success(

f"""

Recommended Actions:

Increase marketing spend in {worst_country.country}.

Invest in improving {worst_category.category} podcast production.

Test shorter episode formats.

"""

)

# ================= BUSINESS QUESTIONS =================

    st.header("Executive Business Questions")

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

"Most Used Platform":

"""

SELECT platform,
COUNT(*) listens

FROM sessions

GROUP BY platform
ORDER BY listens DESC
LIMIT 1

"""

}

    for q,sql in questions.items():

        st.subheader(q)

        df=run_query(sql)

        st.dataframe(df)
