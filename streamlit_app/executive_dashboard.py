import streamlit as st
import plotly.express as px

from database import run_query


def executive_page():
    st.title("Podcast Executive Command Center")

    # ================= KPI SECTION =================
    kpi_query = """
SELECT
    COUNT(DISTINCT s.listener_id) AS active_listeners,
    SUM(s.listen_minutes) AS total_minutes,
    AVG(s.completion_percent) AS avg_completion,
    SUM(CASE WHEN l.subscription_type = 'premium' THEN 1 ELSE 0 END) AS premium_sessions,
    COUNT(*) AS total_sessions
FROM sessions s
JOIN listeners l ON s.listener_id = l.listener_id
"""

    kpis = run_query(kpi_query)
    active_listeners = int(kpis.active_listeners.iloc[0] or 0)
    total_minutes = int(kpis.total_minutes.iloc[0] or 0)
    avg_completion = float(kpis.avg_completion.iloc[0] or 0)
    premium_sessions = int(kpis.premium_sessions.iloc[0] or 0)
    total_sessions = int(kpis.total_sessions.iloc[0] or 0)
    premium_session_share = (premium_sessions / total_sessions * 100) if total_sessions else 0.0

    revenue_query = """
SELECT SUM(revenue_generated) AS revenue
FROM revenue
"""
    revenue = run_query(revenue_query)
    total_revenue = float(revenue.revenue.iloc[0] or 0)

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Active Listeners", f"{active_listeners:,}")
    k2.metric("Listening Minutes", f"{total_minutes:,}")
    k3.metric("Avg Completion", f"{avg_completion:.1f}%")
    k4.metric("Premium Session Share", f"{premium_session_share:.1f}%")
    k5.metric("Total Revenue", f"{total_revenue:,.0f}")

    st.divider()

    # ================= CORE PERFORMANCE =================
    trend_query = """
SELECT
    strftime('%Y-%m', listen_start_time) AS month,
    SUM(listen_minutes) AS minutes
FROM sessions
GROUP BY month
ORDER BY month
"""
    trend = run_query(trend_query)

    if trend.empty:
        st.warning("No listening trend data available.")
        return

    st.plotly_chart(
        px.line(trend, x="month", y="minutes", title="Monthly Listening Trend", markers=True),
        use_container_width=True,
    )

    cat_query = """
SELECT
    p.category,
    SUM(s.listen_minutes) AS minutes
FROM sessions s
JOIN episodes e ON s.episode_id = e.episode_id
JOIN podcasts p ON e.podcast_id = p.podcast_id
GROUP BY p.category
ORDER BY minutes DESC
"""
    cat = run_query(cat_query)

    geo_query = """
SELECT
    l.country,
    SUM(s.listen_minutes) AS minutes
FROM sessions s
JOIN listeners l ON s.listener_id = l.listener_id
GROUP BY l.country
ORDER BY minutes DESC
"""
    geo = run_query(geo_query)

    left, right = st.columns(2)
    with left:
        st.subheader("Category Engagement")
        if cat.empty:
            st.info("No category data available.")
        else:
            st.plotly_chart(px.bar(cat, x="category", y="minutes"), use_container_width=True)

    with right:
        st.subheader("Country Engagement")
        if geo.empty:
            st.info("No country data available.")
        else:
            st.plotly_chart(px.bar(geo, x="country", y="minutes"), use_container_width=True)

    st.divider()

    # ================= SUBSCRIPTION ANALYSIS =================
    st.header("Subscription Analysis")

    sub_mix_query = """
SELECT
    subscription_type,
    COUNT(*) AS listeners
FROM listeners
GROUP BY subscription_type
ORDER BY listeners DESC
"""
    sub_mix = run_query(sub_mix_query)

    sub_trend_query = """
SELECT
    strftime('%Y-%m', signup_date) AS month,
    subscription_type,
    COUNT(*) AS signups
FROM listeners
GROUP BY month, subscription_type
ORDER BY month, subscription_type
"""
    sub_trend = run_query(sub_trend_query)

    sub_country_query = """
SELECT
    l.country,
    COUNT(DISTINCT CASE WHEN l.subscription_type = 'premium' THEN l.listener_id END) AS premium_listeners,
    COUNT(DISTINCT l.listener_id) AS total_listeners,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN l.subscription_type = 'premium' THEN l.listener_id END)
        / NULLIF(COUNT(DISTINCT l.listener_id), 0),
        2
    ) AS premium_penetration_pct
FROM listeners l
GROUP BY l.country
ORDER BY premium_penetration_pct DESC
"""
    sub_country = run_query(sub_country_query)

    sub_platform_query = """
SELECT
    s.platform,
    COUNT(DISTINCT CASE WHEN l.subscription_type = 'premium' THEN s.listener_id END) AS premium_listeners,
    COUNT(DISTINCT s.listener_id) AS all_listeners,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN l.subscription_type = 'premium' THEN s.listener_id END)
        / NULLIF(COUNT(DISTINCT s.listener_id), 0),
        2
    ) AS premium_share_pct
FROM sessions s
JOIN listeners l ON s.listener_id = l.listener_id
GROUP BY s.platform
ORDER BY premium_share_pct DESC
"""
    sub_platform = run_query(sub_platform_query)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Subscription Mix")
        if sub_mix.empty:
            st.info("No subscription mix data available.")
        else:
            st.plotly_chart(
                px.pie(sub_mix, names="subscription_type", values="listeners", hole=0.45),
                use_container_width=True,
            )

    with c2:
        st.subheader("Signup Trend by Type")
        if sub_trend.empty:
            st.info("No signup trend data available.")
        else:
            st.plotly_chart(
                px.line(
                    sub_trend,
                    x="month",
                    y="signups",
                    color="subscription_type",
                    markers=True,
                ),
                use_container_width=True,
            )

    st.subheader("Premium Penetration by Country")
    if sub_country.empty:
        st.info("No country-level subscription data available.")
    else:
        st.dataframe(sub_country, use_container_width=True, hide_index=True)

    st.subheader("Premium Share by Platform")
    if sub_platform.empty:
        st.info("No platform-level subscription data available.")
    else:
        st.plotly_chart(
            px.bar(sub_platform, x="platform", y="premium_share_pct", title="Premium Share % by Platform"),
            use_container_width=True,
        )
        st.dataframe(sub_platform, use_container_width=True, hide_index=True)

    st.divider()

    # ================= BUSINESS QUESTIONS =================
    st.header("Executive Business Questions")

    category_sub_query = """
SELECT
    p.category,
    COUNT(DISTINCT CASE WHEN l.subscription_type = 'premium' THEN s.listener_id END) AS premium_listeners,
    COUNT(DISTINCT s.listener_id) AS all_listeners,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN l.subscription_type = 'premium' THEN s.listener_id END)
        / NULLIF(COUNT(DISTINCT s.listener_id), 0),
        2
    ) AS premium_share_pct
FROM sessions s
JOIN listeners l ON s.listener_id = l.listener_id
JOIN episodes e ON s.episode_id = e.episode_id
JOIN podcasts p ON e.podcast_id = p.podcast_id
GROUP BY p.category
ORDER BY premium_listeners DESC
"""
    category_sub = run_query(category_sub_query)

    episode_sub_query = """
SELECT
    e.episode_title,
    p.category,
    COUNT(DISTINCT CASE WHEN l.subscription_type = 'premium' THEN s.listener_id END) AS premium_listeners,
    SUM(s.listen_minutes) AS listen_minutes
FROM sessions s
JOIN listeners l ON s.listener_id = l.listener_id
JOIN episodes e ON s.episode_id = e.episode_id
JOIN podcasts p ON e.podcast_id = p.podcast_id
GROUP BY e.episode_id, e.episode_title, p.category
ORDER BY premium_listeners DESC, listen_minutes DESC
LIMIT 10
"""
    episode_sub = run_query(episode_sub_query)

    if not category_sub.empty:
        top_category = category_sub.iloc[0]
        st.success(
            f"Category driving subscriptions: {top_category['category']} "
            f"({int(top_category['premium_listeners'])} premium listeners, "
            f"{float(top_category['premium_share_pct'] or 0):.1f}% premium share)."
        )
        st.subheader("Which categories drive subscriptions?")
        st.dataframe(category_sub, use_container_width=True, hide_index=True)
        st.plotly_chart(
            px.bar(
                category_sub,
                x="category",
                y="premium_listeners",
                color="premium_share_pct",
                title="Premium Listeners by Category",
            ),
            use_container_width=True,
        )
    else:
        st.info("No category subscription data available.")

    if not episode_sub.empty:
        top_episode = episode_sub.iloc[0]
        st.success(
            f"Episode driving subscriptions: {top_episode['episode_title']} "
            f"({int(top_episode['premium_listeners'])} premium listeners, category: {top_episode['category']})."
        )
        st.subheader("Which episodes drive subscriptions?")
        st.dataframe(episode_sub, use_container_width=True, hide_index=True)
    else:
        st.info("No episode subscription data available.")
