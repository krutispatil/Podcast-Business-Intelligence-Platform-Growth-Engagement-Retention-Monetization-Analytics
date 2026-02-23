import streamlit as st
from database import run_query
import plotly.express as px
import pandas as pd


def executive_page():

    st.title("Podcast Executive Intelligence")

    # ---------- KPI SECTION ----------

    kpi_query="""

SELECT

COUNT(DISTINCT listener_id) listeners,
COUNT(DISTINCT episode_id) episodes,
SUM(listen_minutes) total_minutes

FROM sessions;

"""

    kpis=run_query(kpi_query)

    col1,col2,col3=st.columns(3)

    col1.metric(

    "Active Listeners",

    int(kpis.listeners.iloc[0])

    )

    col2.metric(

    "Episodes Streamed",

    int(kpis.episodes.iloc[0])

    )

    col3.metric(

    "Listening Minutes",

    int(kpis.total_minutes.iloc[0])

    )

    st.divider()

    # ---------- Revenue by Category ----------

    revenue_query=open(

    "sql_queries/revenue_by_category.sql"

    ).read()

    revenue_df=run_query(revenue_query)

    fig1=px.bar(

    revenue_df,

    x="category",

    y="total_revenue",

    title="Revenue Contribution by Podcast Category"

    )

    st.plotly_chart(fig1,use_container_width=True)

    # ---------- Platform Usage ----------

    platform_query="""

SELECT platform,COUNT(*) listens

FROM sessions

GROUP BY platform

"""

    platform_df=run_query(platform_query)

    fig2=px.pie(

    platform_df,

    names="platform",

    values="listens",

    title="Platform Listening Share"

    )

    st.plotly_chart(fig2,use_container_width=True)

    # ---------- Completion Analysis ----------

    completion_query="""

SELECT

p.category,

AVG(s.completion_percent) avg_completion

FROM sessions s

JOIN episodes e

ON s.episode_id=e.episode_id

JOIN podcasts p

ON e.podcast_id=p.podcast_id

GROUP BY p.category

"""

    completion_df=run_query(completion_query)

    fig3=px.bar(

    completion_df,

    x="category",

    y="avg_completion",

    title="Average Completion Rate"

    )

    st.plotly_chart(fig3,use_container_width=True)

    # ---------- Executive Insight ----------

    top=revenue_df.iloc[0]

    st.success(

    f"Top Revenue Category : {top.category}"

    )
