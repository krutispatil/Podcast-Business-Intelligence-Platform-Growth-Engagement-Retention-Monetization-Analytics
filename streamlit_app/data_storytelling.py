import pandas as pd
import plotly.express as px
import streamlit as st

from database import run_query


def data_storytelling_page():
    st.title("Podcast Data Storytelling")
    st.caption("Narrative-first view: what happened, why it happened, and what we should do next.")

    trend_query = """
SELECT
    strftime('%Y-%m', s.listen_start_time) AS month,
    SUM(s.listen_minutes) AS listen_minutes,
    AVG(s.completion_percent) AS avg_completion
FROM sessions s
GROUP BY month
ORDER BY month
"""

    category_query = """
SELECT
    p.category,
    SUM(s.listen_minutes) AS minutes,
    AVG(s.completion_percent) AS completion
FROM sessions s
JOIN episodes e ON s.episode_id = e.episode_id
JOIN podcasts p ON e.podcast_id = p.podcast_id
GROUP BY p.category
ORDER BY minutes DESC
"""

    country_query = """
SELECT
    l.country,
    SUM(s.listen_minutes) AS minutes,
    AVG(s.completion_percent) AS completion
FROM sessions s
JOIN listeners l ON s.listener_id = l.listener_id
GROUP BY l.country
ORDER BY minutes DESC
"""

    platform_query = """
SELECT
    s.platform,
    SUM(s.listen_minutes) AS minutes,
    AVG(s.completion_percent) AS completion
FROM sessions s
GROUP BY s.platform
ORDER BY minutes DESC
"""

    revenue_query = """
SELECT
    strftime('%Y-%m', s.listen_start_time) AS month,
    SUM(r.revenue_generated) AS revenue
FROM revenue r
JOIN sessions s ON r.episode_id = s.episode_id
GROUP BY month
ORDER BY month
"""

    trend = run_query(trend_query)
    category = run_query(category_query)
    country = run_query(country_query)
    platform = run_query(platform_query)
    revenue = run_query(revenue_query)

    if trend.empty:
        st.warning("No storytelling data available yet.")
        return

    trend["listen_minutes"] = trend["listen_minutes"].fillna(0)
    trend["avg_completion"] = trend["avg_completion"].fillna(0)
    trend["mom_change"] = trend["listen_minutes"].diff().fillna(0)
    trend["rolling_3m"] = trend["listen_minutes"].rolling(3, min_periods=1).mean()

    peak_idx = trend["listen_minutes"].idxmax()
    drop_idx = trend["mom_change"].idxmin()

    peak_month = trend.loc[peak_idx, "month"]
    peak_minutes = int(trend.loc[peak_idx, "listen_minutes"])
    drop_month = trend.loc[drop_idx, "month"]
    drop_value = int(trend.loc[drop_idx, "mom_change"])

    total_minutes = int(trend["listen_minutes"].sum())
    latest_completion = float(trend.iloc[-1]["avg_completion"])

    top_category = category.iloc[0] if not category.empty else None
    weak_category = category.iloc[-1] if not category.empty else None
    top_country = country.iloc[0] if not country.empty else None
    weak_country = country.iloc[-1] if not country.empty else None
    weak_platform = platform.sort_values("completion").iloc[0] if not platform.empty else None

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Listen Minutes", f"{total_minutes:,}")
    k2.metric("Peak Month", peak_month)
    k3.metric("Peak Volume", f"{peak_minutes:,}")
    k4.metric("Latest Avg Completion", f"{latest_completion:.1f}%")

    st.subheader("Story Timeline")
    timeline = px.line(
        trend,
        x="month",
        y=["listen_minutes", "rolling_3m"],
        title="Listening Momentum vs 3-Month Baseline",
        markers=True,
    )
    timeline.update_layout(legend_title_text="Series")
    st.plotly_chart(timeline, use_container_width=True)

    st.subheader("Key Story Events")
    events = [
        {
            "Event": "Demand peak",
            "Detail": f"Listening hit {peak_minutes:,} minutes in {peak_month}.",
            "Business Impact": "Best month to replicate channel and content mix.",
        },
        {
            "Event": "Largest MoM decline",
            "Detail": f"A change of {drop_value:,} minutes occurred in {drop_month}.",
            "Business Impact": "Investigate distribution cadence and episode format in prior month.",
        },
    ]

    if top_category is not None and weak_category is not None:
        events.append(
            {
                "Event": "Category polarization",
                "Detail": (
                    f"{top_category['category']} leads ({int(top_category['minutes']):,} min) while "
                    f"{weak_category['category']} trails ({int(weak_category['minutes']):,} min)."
                ),
                "Business Impact": "Rebalance production to protect downside categories.",
            }
        )

    if top_country is not None and weak_country is not None:
        events.append(
            {
                "Event": "Geographic concentration",
                "Detail": (
                    f"{top_country['country']} is strongest ({int(top_country['minutes']):,} min), "
                    f"{weak_country['country']} is weakest ({int(weak_country['minutes']):,} min)."
                ),
                "Business Impact": "Localize growth playbooks for underperforming markets.",
            }
        )

    st.dataframe(pd.DataFrame(events), use_container_width=True, hide_index=True)

    left, right = st.columns(2)

    with left:
        st.subheader("Drivers: Category")
        if category.empty:
            st.info("No category data available.")
        else:
            fig_category = px.bar(
                category,
                x="category",
                y="minutes",
                color="completion",
                title="Engagement by Category",
            )
            st.plotly_chart(fig_category, use_container_width=True)

    with right:
        st.subheader("Drivers: Geography")
        if country.empty:
            st.info("No country data available.")
        else:
            fig_country = px.bar(
                country,
                x="country",
                y="minutes",
                color="completion",
                title="Engagement by Country",
            )
            st.plotly_chart(fig_country, use_container_width=True)

    st.subheader("Action Tracker")
    actions = [
        {
            "Priority": "P1",
            "Initiative": "Stabilize weak categories",
            "Owner": "Content Lead",
            "Metric": "Minutes in bottom category",
            "Target": "+15% in 6 weeks",
            "Status": "Planned",
        },
        {
            "Priority": "P1",
            "Initiative": "Recover decline month playbook",
            "Owner": "Growth Lead",
            "Metric": "MoM minute change",
            "Target": "Back to non-negative MoM",
            "Status": "In Progress",
        },
    ]

    if weak_country is not None:
        actions.append(
            {
                "Priority": "P2",
                "Initiative": f"Localized campaign for {weak_country['country']}",
                "Owner": "Regional Marketing",
                "Metric": f"Minutes in {weak_country['country']}",
                "Target": "+20% in 8 weeks",
                "Status": "Planned",
            }
        )

    if weak_platform is not None:
        actions.append(
            {
                "Priority": "P2",
                "Initiative": f"Completion uplift on {weak_platform['platform']}",
                "Owner": "Product",
                "Metric": f"Completion on {weak_platform['platform']}",
                "Target": "+5 pts in 1 quarter",
                "Status": "Planned",
            }
        )

    st.dataframe(pd.DataFrame(actions), use_container_width=True, hide_index=True)

    st.subheader("Revenue Context")
    if revenue.empty:
        st.info("No revenue trend available.")
    else:
        revenue["revenue"] = revenue["revenue"].fillna(0)
        revenue_fig = px.area(
            revenue,
            x="month",
            y="revenue",
            title="Revenue Trend (Monthly)",
        )
        st.plotly_chart(revenue_fig, use_container_width=True)
