import streamlit as st
import pandas as pd

# ============================
# Load predictions
# ============================
preds = pd.read_csv("predictions_with_scores.csv")

st.title("🏈 College Football Model Predictions")

# ============================
# Search bar
# ============================
search = st.text_input("🔍 Search for a team:")

# ============================
# Calculate model margin + scores
# ============================
preds["proj_margin"] = preds["proj_home_score"] - preds["proj_away_score"]

def project_score(row):
    if pd.isna(row["consensus_total"]):
        return "N/A"
    total = row["consensus_total"]
    margin = row["proj_margin"]
    home_score = (total / 2) + (margin / 2)
    away_score = (total / 2) - (margin / 2)
    return f"{int(round(home_score))} - {int(round(away_score))}"

preds["Projected Score"] = preds.apply(project_score, axis=1)

# ============================
# Clean display table
# ============================
def format_team_with_spread(row, home=True):
    if pd.isna(row["consensus_spread"]):
        return row["homeTeam"] if home else row["awayTeam"]
    if home:
        return f"{row['homeTeam']} ({row['consensus_spread']:+})"
    else:
        return f"{row['awayTeam']} ({-row['consensus_spread']:+})"

preds["Home Team"] = preds.apply(lambda r: format_team_with_spread(r, home=True), axis=1)
preds["Away Team"] = preds.apply(lambda r: format_team_with_spread(r, home=False), axis=1)

preds["Projected Winner"] = preds.apply(
    lambda r: r["homeTeam"] if r["proj_margin"] >= 0 else r["awayTeam"], axis=1
)

display_df = preds[["Home Team", "Away Team", "Projected Winner", "Projected Score"]]

if search:
    display_df = display_df[
        display_df["Home Team"].str.contains(search, case=False)
        | display_df["Away Team"].str.contains(search, case=False)
    ]

st.markdown("### 📊 Predictions Table")
st.write("Swipe left/right on mobile to view all columns 👇")
st.dataframe(display_df, use_container_width=True)

# ============================
# 🔥 Best Bets Board
# ============================
st.markdown("## 🔥 Best Bets Board (Top 10)")

# Edge vs line
preds["edge"] = preds["proj_margin"] - preds["consensus_spread"]
preds["confidence"] = preds["edge"].abs().round(2)

def best_bet_pick(row):
    if row["edge"] > 0:
        return f"{row['homeTeam']} {row['consensus_spread']:+}"
    else:
        return f"{row['awayTeam']} {(-row['consensus_spread']):+}"

preds["Pick"] = preds.apply(best_bet_pick, axis=1)

board = preds.sort_values("confidence", ascending=False).head(10)[
    ["Pick", "confidence", "edge", "Projected Score"]
]

board = board.rename(
    columns={
        "Pick": "📌 Pick",
        "confidence": "✅ Confidence (Edge)",
        "edge": "📊 Edge vs Line",
        "Projected Score": "📈 Projected Score",
    }
)

# Highlight stronger edges
def highlight_confidence(val):
    if val > 10:
        return "background-color: #90EE90"  # green
    elif val > 5:
        return "background-color: #FFFF99"  # yellow
    return ""

st.table(board.style.applymap(highlight_confidence, subset=["✅ Confidence (Edge)"]))



