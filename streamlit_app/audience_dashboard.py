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
