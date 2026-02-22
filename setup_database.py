import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("sqlite:///database/podcast.db")

podcasts = pd.read_csv("data/podcasts.csv")
episodes = pd.read_csv("data/episodes.csv")
listeners = pd.read_csv("data/listeners.csv")
sessions = pd.read_csv("data/listening_sessions.csv")
revenue = pd.read_csv("data/revenue.csv")

podcasts.to_sql("podcasts",engine,if_exists="replace",index=False)
episodes.to_sql("episodes",engine,if_exists="replace",index=False)
listeners.to_sql("listeners",engine,if_exists="replace",index=False)
sessions.to_sql("sessions",engine,if_exists="replace",index=False)
revenue.to_sql("revenue",engine,if_exists="replace",index=False)

print("Database Created Successfully")
