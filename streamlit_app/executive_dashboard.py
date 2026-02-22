import streamlit as st
from database import run_query
import plotly.express as px

def executive_page():

    st.title("Executive Overview")

    query=open("sql_queries/revenue_by_category.sql").read()

    df=run_query(query)

    fig=px.bar(

    df,

    x="category",

    y="total_revenue",

    title="Revenue by Category"

    )

    st.plotly_chart(fig,use_container_width=True)
