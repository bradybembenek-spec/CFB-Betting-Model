import streamlit as st
import pandas as pd

# Load predictions
preds = pd.read_csv("predictions_upcoming_full.csv")

st.title("🏈 College Football Model Predictions")

# --- Search bar ---
search = st.text_input("🔍 Search for a team:")

# --- Clean columns ---
# Calculate projected scores (simple version: spread splits total points)
def project_scores(row):
    if pd.notna(row["consensus_spread"]) and pd.notna(row["consensus_total"]):
        home_score = round((row["consensus_total"] / 2) - (row["consensus_spread"] / 2))
        away_score = round((row["consensus_total"] / 2) + (row["consensus_spread"] / 2))
        return f"{int(home_score)} - {int(away_score)}"
    else:
        return "N/A"

preds["Projected Score"] = preds.apply(project_scores, axis=1)

# Format team names with spreads
def format_team(name, spread, home=True):
    if pd.isna(spread):
        return name
    spread_str = f"{spread:+}" if home else f"{-spread:+}"
    return f"{name} ({spread_str})"

preds["Home Team"] = preds.apply(lambda r: format_team(r["homeTeam"], r["consensus_spread"], home=True), axis=1)
preds["Away Team"] = preds.apply(lambda r: format_team(r["awayTeam"], r["consensus_spread"], home=False), axis=1)

# Determine projected winner
preds["Projected Winner"] = preds.apply(
    lambda r: r["homeTeam"] if r["home_win_prob"] >= 0.5 else r["awayTeam"], axis=1
)

# --- Add team logos (simple placeholder version using ESPN logo links) ---
# Example: https://a.espncdn.com/i/teamlogos/ncaa/500/61.png
def team_logo_url(team_name):
    # This is a placeholder map - you'd expand it with your actual team dataset
    logos = {
        "Georgia": "https://a.espncdn.com/i/teamlogos/ncaa/500/61.png",
        "Georgia Tech": "https://a.espncdn.com/i/teamlogos/ncaa/500/59.png",
        "Alabama": "https://a.espncdn.com/i/teamlogos/ncaa/500/333.png",
    }
    return logos.get(team_name, "https://a.espncdn.com/i/teamlogos/ncaa/500/default.png")

preds["Winner Logo"] = preds["Projected Winner"].apply(team_logo_url)

# Build final display dataframe
display_df = preds[["Home Team", "Away Team", "Projected Winner", "Projected Score", "Winner Logo"]]

# --- Apply search filter ---
if search:
    display_df = display_df[
        display_df["Home Team"].str.contains(search, case=False) |
        display_df["Away Team"].str.contains(search, case=False)
    ]

# --- Display table ---
st.dataframe(display_df, use_container_width=True)



