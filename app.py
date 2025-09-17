import streamlit as st
import pandas as pd

st.set_page_config(page_title="CFB Predictions", layout="wide")
st.title("🏈 College Football Betting Model")

# Load predictions
@st.cache_data
def load_data():
    return pd.read_csv("predictions_upcoming_full.csv")

df = load_data()

# ---- Process for clean table ----
df["Win %"] = (df["home_win_prob"] * 100).round(1)
df["Cover %"] = (df["home_cover_prob"] * 100).round(1)
df["Over %"] = (df["over_prob"] * 100).round(1)

# Projected Winner
df["Projected Winner"] = df.apply(
    lambda row: row["homeTeam"] if row["home_win_prob"] >= 0.5 else row["awayTeam"],
    axis=1
)

# Projected Team to Cover
df["Projected Cover"] = df.apply(
    lambda row: row["homeTeam"] if row["home_cover_prob"] >= 0.5 else row["awayTeam"],
    axis=1
)

# Projected Score (simple estimate)
df["Home Score"] = ((df["consensus_total"] + df["consensus_spread"]) / 2).round(0)
df["Away Score"] = (df["consensus_total"] - df["Home Score"]).round(0)
df["Projected Score"] = df["Home Score"].astype(int).astype(str) + " - " + df["Away Score"].astype(int).astype(str)

# ---- Final clean table ----
table = df[[
    "homeTeam",
    "awayTeam",
    "consensus_spread",
    "Projected Winner",
    "Projected Cover",
    "Projected Score"
]].rename(columns={
    "homeTeam": "Home Team",
    "awayTeam": "Away Team",
    "consensus_spread": "Spread"
})

# Show table
st.subheader("📅 Model Projections")
st.dataframe(table, use_container_width=True)

