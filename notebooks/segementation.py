import pandas as pd
from sqlalchemy import create_engine
from sklearn.cluster import KMeans

engine = create_engine("sqlite:///database/podcast.db")

sessions=pd.read_sql("SELECT * FROM sessions",engine)

agg=sessions.groupby("listener_id").agg({

"listen_minutes":"sum",
"completion_percent":"mean",
"session_id":"count"

}).reset_index()

agg.columns=["listener_id","total_minutes","avg_completion","sessions"]

model=KMeans(n_clusters=3,random_state=42)

agg["segment"]=model.fit_predict(

agg[["total_minutes","avg_completion","sessions"]]

)

agg.to_csv("data/listener_segments.csv",index=False)

print("Segmentation Saved")
