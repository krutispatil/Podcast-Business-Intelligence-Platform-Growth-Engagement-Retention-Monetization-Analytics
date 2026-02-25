import streamlit as st
from database import run_query

TABLE_DESCRIPTIONS = {
    "podcasts": "Master list of shows and their metadata.",
    "episodes": "Episode-level metadata linked to podcasts.",
    "listeners": "User profile and subscription details.",
    "sessions": "Listening events by listener and episode.",
    "revenue": "Monetization outcomes per episode.",
}

SCHEMA = {
    "podcasts": ["podcast_id", "podcast_name", "category", "language", "launch_date"],
    "episodes": [
        "episode_id",
        "podcast_id",
        "episode_title",
        "publish_date",
        "duration_minutes",
        "guest_type",
    ],
    "listeners": [
        "listener_id",
        "country",
        "age_group",
        "gender",
        "subscription_type",
        "signup_date",
    ],
    "sessions": [
        "session_id",
        "listener_id",
        "episode_id",
        "listen_start_time",
        "listen_minutes",
        "completion_percent",
        "device",
        "platform",
    ],
    "revenue": ["episode_id", "ads_shown", "ads_clicked", "revenue_generated"],
}

QUERY_TEMPLATES = {
    "Top categories by listening minutes": """
SELECT
    p.category,
    SUM(s.listen_minutes) AS total_minutes
FROM sessions s
JOIN episodes e ON s.episode_id = e.episode_id
JOIN podcasts p ON e.podcast_id = p.podcast_id
GROUP BY p.category
ORDER BY total_minutes DESC;
""",
    "Premium vs free listener mix": """
SELECT
    subscription_type,
    COUNT(*) AS listeners
FROM listeners
GROUP BY subscription_type
ORDER BY listeners DESC;
""",
    "Monthly listening trend": """
SELECT
    strftime('%Y-%m', listen_start_time) AS month,
    SUM(listen_minutes) AS minutes
FROM sessions
GROUP BY month
ORDER BY month;
""",
    "Top 10 episodes by revenue": """
SELECT
    e.episode_title,
    SUM(r.revenue_generated) AS revenue
FROM revenue r
JOIN episodes e ON r.episode_id = e.episode_id
GROUP BY e.episode_id, e.episode_title
ORDER BY revenue DESC
LIMIT 10;
""",
}


def _table_count(table_name):
    count_df = run_query(f"SELECT COUNT(*) AS rows_count FROM {table_name}")
    return int(count_df.rows_count.iloc[0] or 0)


def sql_explorer():
    st.title("SQL Explorer")
    st.caption("Explore schema, preview tables, and run custom SQL to understand your podcast business data.")

    st.subheader("Data Dictionary")
    for table, cols in SCHEMA.items():
        with st.expander(f"{table}"):
            st.write(TABLE_DESCRIPTIONS.get(table, ""))
            st.write(f"Columns: {', '.join(cols)}")
            st.write(f"Row count: {_table_count(table):,}")

    st.subheader("Table Preview")
    selected_table = st.selectbox("Select table", list(SCHEMA.keys()))
    preview_limit = st.slider("Rows to preview", min_value=5, max_value=100, value=20, step=5)
    preview_df = run_query(f"SELECT * FROM {selected_table} LIMIT {preview_limit}")
    st.dataframe(preview_df, use_container_width=True)

    st.subheader("Starter Queries")
    selected_template = st.selectbox("Choose a starter query", list(QUERY_TEMPLATES.keys()))
    st.code(QUERY_TEMPLATES[selected_template].strip(), language="sql")

    st.subheader("Custom SQL")
    default_sql = QUERY_TEMPLATES[selected_template].strip()
    query = st.text_area("Write SQL query", value=default_sql, height=220)

    if st.button("Run Query"):
        try:
            result = run_query(query)
            st.success(f"Returned {len(result)} rows.")
            st.dataframe(result, use_container_width=True)
        except Exception as e:
            st.error(f"Query failed: {e}")
