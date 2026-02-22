from sqlalchemy import create_engine
import pandas as pd

engine=create_engine("sqlite:///database/podcast.db")

def run_query(query):

    return pd.read_sql(query,engine)
