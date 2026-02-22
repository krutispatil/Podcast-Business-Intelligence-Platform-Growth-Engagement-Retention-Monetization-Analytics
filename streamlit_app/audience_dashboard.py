import streamlit as st
import pandas as pd
import plotly.express as px

def audience_page():

    st.title("Audience Segments")

    df=pd.read_csv("data/listener_segments.csv")

    fig=px.scatter(

    df,

    x="total_minutes",

    y="avg_completion",

    color="segment"

    )

    st.plotly_chart(fig,use_container_width=True)
