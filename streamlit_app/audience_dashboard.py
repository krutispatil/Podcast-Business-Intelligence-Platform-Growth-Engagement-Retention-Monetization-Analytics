import streamlit as st
import pandas as pd
import plotly.express as px


def _root_cause_for_risk_segment(seg_row, overall_completion, overall_sessions):
    completion = float(seg_row["avg_completion"])
    sessions = float(seg_row["sessions"])

    if completion < overall_completion and sessions < overall_sessions:
        return (
            "Low completion and low sessions suggest weak content-market fit and weak habit formation. "
            "Listeners likely drop early and do not return consistently."
        )
    if completion < overall_completion and sessions >= overall_sessions:
        return (
            "Listeners are coming back, but completion is still low. This points to episode format issues "
            "(length/pacing/topic relevance) more than discovery issues."
        )
    return (
        "Engagement is uneven rather than strictly low; segment behavior suggests friction in the listening journey "
        "such as device/platform UX gaps or inconsistent episode quality."
    )


def _root_cause_for_growth_segment(seg_row, overall_completion, overall_sessions):
    completion = float(seg_row["avg_completion"])
    sessions = float(seg_row["sessions"])

    if completion >= overall_completion and sessions >= overall_sessions:
        return (
            "High completion and high session frequency indicate strong content resonance and repeat behavior. "
            "This segment has both content fit and habit strength."
        )
    if completion >= overall_completion and sessions < overall_sessions:
        return (
            "Content is resonating (high completion), but session frequency is still developing. "
            "This segment likely needs better cadence nudges to become heavy listeners."
        )
    return (
        "Listening volume is strong despite mixed completion, which suggests successful discovery/distribution "
        "but room to improve content retention quality."
    )


def audience_page():
    st.title("Audience Segments")

    df = pd.read_csv("data/listener_segments.csv")
    if df.empty:
        st.warning("No audience segment data available.")
        return

    df["segment"] = df["segment"].astype(str)

    overall_minutes = float(df["total_minutes"].mean())
    overall_completion = float(df["avg_completion"].mean())
    overall_sessions = float(df["sessions"].mean())

    fig = px.scatter(
        df,
        x="total_minutes",
        y="avg_completion",
        color="segment",
        size="sessions",
        title="Audience Segments: Depth vs Retention",
        hover_data=["listener_id", "sessions"],
    )
    fig.add_vline(
        x=overall_minutes,
        line_dash="dash",
        line_color="gray",
        annotation_text="Avg minutes",
        annotation_position="top left",
    )
    fig.add_hline(
        y=overall_completion,
        line_dash="dash",
        line_color="gray",
        annotation_text="Avg completion",
        annotation_position="top right",
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("How to read this chart"):
        st.markdown(
            "- `X-axis (total_minutes)`: further right means deeper listening.\n"
            "- `Y-axis (avg_completion)`: higher means better episode retention.\n"
            "- `Bubble size (sessions)`: larger bubbles return more often.\n"
            "- Dashed lines are overall averages, creating 4 quadrants for fast diagnosis."
        )

    segment_summary = (
        df.groupby("segment", as_index=False)
        .agg(
            listeners=("listener_id", "count"),
            total_minutes=("total_minutes", "mean"),
            avg_completion=("avg_completion", "mean"),
            sessions=("sessions", "mean"),
        )
        .sort_values("total_minutes", ascending=False)
    )
    segment_summary["listener_share_pct"] = (
        segment_summary["listeners"] / segment_summary["listeners"].sum() * 100
    )

    st.subheader("Segment Summary")
    st.dataframe(
        segment_summary.round(
            {
                "total_minutes": 1,
                "avg_completion": 1,
                "sessions": 1,
                "listener_share_pct": 1,
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    growth_seg = segment_summary.sort_values(
        ["total_minutes", "avg_completion"], ascending=False
    ).iloc[0]
    risk_seg = segment_summary.sort_values(
        ["avg_completion", "total_minutes"], ascending=[True, True]
    ).iloc[0]

    high_completion_low_minutes = segment_summary[
        (segment_summary["avg_completion"] >= overall_completion)
        & (segment_summary["total_minutes"] < overall_minutes)
    ]
    opportunity_seg = (
        high_completion_low_minutes.sort_values("avg_completion", ascending=False).iloc[0]
        if not high_completion_low_minutes.empty
        else None
    )

    st.subheader("What Is Happening")
    st.info(
        f"Segment **{growth_seg['segment']}** leads engagement with "
        f"~**{growth_seg['total_minutes']:.0f}** minutes and **{growth_seg['avg_completion']:.1f}%** completion. "
        f"Segment **{risk_seg['segment']}** is the weakest with "
        f"~**{risk_seg['total_minutes']:.0f}** minutes and **{risk_seg['avg_completion']:.1f}%** completion."
    )

    st.subheader("Root-Cause Analysis")
    st.warning(
        f"Risk segment root cause (Segment {risk_seg['segment']}): "
        + _root_cause_for_risk_segment(risk_seg, overall_completion, overall_sessions)
    )
    st.success(
        f"Growth segment root cause (Segment {growth_seg['segment']}): "
        + _root_cause_for_growth_segment(growth_seg, overall_completion, overall_sessions)
    )

    st.subheader("Actionable Insights")
    actions = [
        {
            "Priority": "P1",
            "Action": f"Launch retention fixes for Segment {risk_seg['segment']}",
            "Why": "This segment has the lowest completion and/or listening depth.",
            "How": "Test shorter episode cuts, stronger first 5 minutes, and tighter topic targeting.",
            "Success Metric": "+8-10 pts completion in 4-6 weeks",
        },
        {
            "Priority": "P1",
            "Action": f"Scale acquisition around Segment {growth_seg['segment']}",
            "Why": "This segment shows the strongest engagement quality.",
            "How": "Replicate top episode themes/guests/channels that over-index in this segment.",
            "Success Metric": "+15% listener volume in high-performing segment",
        },
    ]

    if opportunity_seg is not None:
        actions.append(
            {
                "Priority": "P2",
                "Action": f"Increase session frequency for Segment {opportunity_seg['segment']}",
                "Why": "High completion but below-average minutes indicates unrealized upside.",
                "How": "Use episodic reminders, sequence playlists, and weekly habit nudges.",
                "Success Metric": "+20% sessions with stable completion",
            }
        )

    actions_df = pd.DataFrame(actions)
    st.dataframe(actions_df, use_container_width=True, hide_index=True)

    st.divider()

    # ================= DEMOGRAPHIC INSIGHTS =================
    st.header("Demographic Insights")
    listeners = pd.read_csv("data/listeners.csv")
    audience_demo = df.merge(listeners, on="listener_id", how="left")
    audience_demo = audience_demo.dropna(subset=["age_group", "country", "gender", "subscription_type"])

    if audience_demo.empty:
        st.info("No demographic data available.")
        return

    age_stats = (
        audience_demo.groupby("age_group", as_index=False)
        .agg(
            listeners=("listener_id", "count"),
            avg_minutes=("total_minutes", "mean"),
            avg_completion=("avg_completion", "mean"),
            avg_sessions=("sessions", "mean"),
            premium_listeners=("subscription_type", lambda x: (x == "premium").sum()),
        )
    )
    age_stats["premium_penetration_pct"] = (
        age_stats["premium_listeners"] / age_stats["listeners"] * 100
    )

    country_stats = (
        audience_demo.groupby("country", as_index=False)
        .agg(
            listeners=("listener_id", "count"),
            avg_minutes=("total_minutes", "mean"),
            avg_completion=("avg_completion", "mean"),
            premium_listeners=("subscription_type", lambda x: (x == "premium").sum()),
        )
    )
    country_stats["premium_penetration_pct"] = (
        country_stats["premium_listeners"] / country_stats["listeners"] * 100
    )

    gender_stats = (
        audience_demo.groupby("gender", as_index=False)
        .agg(
            listeners=("listener_id", "count"),
            avg_minutes=("total_minutes", "mean"),
            avg_completion=("avg_completion", "mean"),
        )
        .sort_values("listeners", ascending=False)
    )

    d1, d2 = st.columns(2)
    with d1:
        st.subheader("Age Group Distribution")
        st.plotly_chart(
            px.bar(
                age_stats.sort_values("listeners", ascending=False),
                x="age_group",
                y="listeners",
                color="premium_penetration_pct",
                title="Audience Size and Premium Penetration by Age",
            ),
            use_container_width=True,
        )

    with d2:
        st.subheader("Top Countries")
        st.plotly_chart(
            px.bar(
                country_stats.sort_values("listeners", ascending=False).head(10),
                x="country",
                y="listeners",
                color="premium_penetration_pct",
                title="Top 10 Markets by Listener Base",
            ),
            use_container_width=True,
        )

    d3, d4 = st.columns(2)
    with d3:
        st.subheader("Gender Mix")
        st.plotly_chart(
            px.pie(gender_stats, names="gender", values="listeners", hole=0.45),
            use_container_width=True,
        )
    with d4:
        st.subheader("Engagement by Age")
        st.plotly_chart(
            px.bar(
                age_stats.sort_values("avg_minutes", ascending=False),
                x="age_group",
                y="avg_minutes",
                color="avg_completion",
                title="Average Listening Depth by Age",
            ),
            use_container_width=True,
        )

    st.subheader("Demographic Summary Tables")
    t1, t2 = st.columns(2)
    with t1:
        st.dataframe(
            age_stats.sort_values("listeners", ascending=False).round(1),
            use_container_width=True,
            hide_index=True,
        )
    with t2:
        st.dataframe(
            country_stats.sort_values("listeners", ascending=False).head(15).round(1),
            use_container_width=True,
            hide_index=True,
        )

    dominant_age = age_stats.sort_values("listeners", ascending=False).iloc[0]
    growth_age = age_stats.sort_values(["avg_minutes", "avg_completion"], ascending=False).iloc[0]
    risk_age = age_stats.sort_values(["avg_completion", "avg_minutes"], ascending=[True, True]).iloc[0]
    top_country = country_stats.sort_values("listeners", ascending=False).iloc[0]
    low_premium_country = country_stats.sort_values("premium_penetration_pct", ascending=True).iloc[0]

    st.subheader("What Demographics Tell Us")
    st.info(
        f"Largest audience cohort is **{dominant_age['age_group']}** "
        f"({int(dominant_age['listeners'])} listeners). "
        f"Highest engagement cohort is **{growth_age['age_group']}** "
        f"(~{growth_age['avg_minutes']:.0f} minutes, {growth_age['avg_completion']:.1f}% completion). "
        f"Top market by audience size is **{top_country['country']}** "
        f"({int(top_country['listeners'])} listeners)."
    )

    st.subheader("Root-Cause Signals")
    st.warning(
        f"Risk signal: **{risk_age['age_group']}** has the weakest engagement "
        f"({risk_age['avg_completion']:.1f}% completion, {risk_age['avg_minutes']:.0f} minutes). "
        "Likely causes are lower content relevance for this life stage or mismatch in episode length and cadence."
    )
    st.warning(
        f"Monetization gap: **{low_premium_country['country']}** shows low premium penetration "
        f"({low_premium_country['premium_penetration_pct']:.1f}%). "
        "Likely causes include localized pricing/value mismatch or weak premium proposition in this market."
    )

    st.subheader("Demographic Actionable Insights")
    demographic_actions = pd.DataFrame(
        [
            {
                "Priority": "P1",
                "Action": f"Create age-specific content tracks for {risk_age['age_group']}",
                "Why": "This cohort has the lowest retention quality.",
                "Metric": "Avg completion in cohort",
                "Target": "+8 pts in 6 weeks",
            },
            {
                "Priority": "P1",
                "Action": f"Scale campaigns in {top_country['country']}",
                "Why": "Largest market can yield fastest absolute growth.",
                "Metric": "New listeners from top market",
                "Target": "+15% in 1 quarter",
            },
            {
                "Priority": "P2",
                "Action": f"Improve premium conversion in {low_premium_country['country']}",
                "Why": "Market has audience but under-converts to premium.",
                "Metric": "Premium penetration",
                "Target": "+5 pts in 1 quarter",
            },
            {
                "Priority": "P2",
                "Action": f"Double down on {growth_age['age_group']} engagement formats",
                "Why": "This cohort already demonstrates strong depth and retention.",
                "Metric": "Average minutes per listener",
                "Target": "+10% with stable completion",
            },
        ]
    )
    st.dataframe(demographic_actions, use_container_width=True, hide_index=True)
