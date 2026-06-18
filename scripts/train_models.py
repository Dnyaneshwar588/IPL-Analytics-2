import os
import json
import pickle
import numpy as np
import pandas as pd
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.metrics import accuracy_score, roc_auc_score, mean_squared_error, classification_report
from xgboost import XGBClassifier
from lightgbm import LGBMRegressor

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/ipl_analytics")
client = MongoClient(MONGO_URI)
db = client["ipl_analytics"]

# Ensure directories exist
os.makedirs("ml_service/models", exist_ok=True)

print("Fetching matches and deliveries from MongoDB...")
matches_cursor = db["matches"].find()
matches_df = pd.DataFrame(list(matches_cursor))

deliveries_cursor = db["deliveries"].find()
deliveries_df = pd.DataFrame(list(deliveries_cursor))

if matches_df.empty or deliveries_df.empty:
    print("Error: Matches or Deliveries collection is empty. Please run seed_db.js first.")
    exit(1)

# Drop MongoDB ObjectID
matches_df = matches_df.drop(columns=["_id"])
deliveries_df = deliveries_df.drop(columns=["_id"])

# Sort matches chronologically
matches_df = matches_df.sort_values("date").reset_index(drop=True)

# Define valid wicket kinds for bowling statistics
VALID_WICKET_KINDS = {
    "bowled", "caught", "lbw", "stumped", "caught and bowled", "hit wicket"
}

# Define team name mapping and venue mapping for label encoding
all_teams = sorted(list(set(matches_df["team1"].unique()) | set(matches_df["team2"].unique())))
team_to_idx = {team: idx for idx, team in enumerate(all_teams)}

all_venues = sorted(list(matches_df["venue"].unique()))
venue_to_idx = {venue: idx for idx, venue in enumerate(all_venues)}

# Save mappings
mappings = {
    "team_to_idx": team_to_idx,
    "venue_to_idx": venue_to_idx
}
with open("ml_service/models/mappings.json", "w") as f:
    json.dump(mappings, f, indent=2)

print(f"Team mapping and venue mapping saved. Total Teams: {len(all_teams)}, Total Venues: {len(all_venues)}")

# ==========================================
# 1. Feature Engineering for Match Winner Classifier
# ==========================================
print("Engineering features for Match Winner Classifier...")
match_winner_data = []

# To avoid leakage, calculate cumulative stats chronologically
team_history = {team: {"matches": 0, "wins": 0, "recent_results": []} for team in all_teams}
h2h_history = {}  # key: (teamA, teamB) sorted, value: {teamA_wins, teamB_wins, total}

# Pre-calculate venue average score
venue_scores = deliveries_df[deliveries_df["inning"] == 1].groupby(["matchId", "battingTeam"])["totalRuns"].sum().reset_index()
venue_scores_with_venue = venue_scores.merge(matches_df[["matchId", "venue"]], on="matchId")
venue_avg_scores = venue_scores_with_venue.groupby("venue")["totalRuns"].mean().to_dict()

for idx, match in matches_df.iterrows():
    m_id = match["matchId"]
    team1 = match["team1"]
    team2 = match["team2"]
    winner = match["winner"]
    venue = match["venue"]
    toss_winner = match["tossWinner"]
    toss_decision = match["tossDecision"]
    season = match["season"]

    if winner == "No Result" or not winner:
        continue

    # 1. Cumulative Win Rates
    t1_stats = team_history[team1]
    t2_stats = team_history[team2]

    t1_win_rate = t1_stats["wins"] / t1_stats["matches"] if t1_stats["matches"] > 0 else 0.5
    t2_win_rate = t2_stats["wins"] / t2_stats["matches"] if t2_stats["matches"] > 0 else 0.5

    # 2. Head-to-Head Win Rate (t1 wins / total h2h)
    h2h_key = tuple(sorted([team1, team2]))
    if h2h_key not in h2h_history:
        h2h_history[h2h_key] = {team1: 0, team2: 0, "total": 0}
    
    h2h = h2h_history[h2h_key]
    h2h_win_rate = h2h[team1] / h2h["total"] if h2h["total"] > 0 else 0.5

    # 3. Venue Average First Innings Score
    venue_avg = venue_avg_scores.get(venue, 160.0)

    # 4. Toss Features
    toss_winner_is_team1 = 1 if toss_winner == team1 else 0
    toss_decision_bat = 1 if toss_decision == "bat" else 0

    # 5. Form (rolling last 5 matches win rate)
    form_t1 = sum(t1_stats["recent_results"][-5:]) / len(t1_stats["recent_results"][-5:]) if t1_stats["recent_results"] else 0.5
    form_t2 = sum(t2_stats["recent_results"][-5:]) / len(t2_stats["recent_results"][-5:]) if t2_stats["recent_results"] else 0.5

    # Target: 1 if team1 wins, 0 if team2 wins
    target = 1 if winner == team1 else 0

    try:
        season_encoded = int(season)
    except:
        season_encoded = 2008

    match_winner_data.append({
        "team1_win_rate": t1_win_rate,
        "team2_win_rate": t2_win_rate,
        "h2h_win_rate": h2h_win_rate,
        "venue_avg_score": venue_avg,
        "toss_winner_is_team1": toss_winner_is_team1,
        "toss_decision_bat": toss_decision_bat,
        "form_last5_team1": form_t1,
        "form_last5_team2": form_t2,
        "season_encoded": season_encoded,
        "winner": target
    })

    # Update history
    t1_stats["matches"] += 1
    t2_stats["matches"] += 1
    if winner == team1:
        t1_stats["wins"] += 1
        t1_stats["recent_results"].append(1)
        t2_stats["recent_results"].append(0)
        h2h[team1] += 1
    else:
        t2_stats["wins"] += 1
        t1_stats["recent_results"].append(0)
        t2_stats["recent_results"].append(1)
        h2h[team2] += 1
    h2h["total"] += 1

mw_df = pd.DataFrame(match_winner_data)

# Split and train Match Winner
X_mw = mw_df.drop(columns=["winner"])
y_mw = mw_df["winner"]

X_train_mw, X_test_mw, y_train_mw, y_test_mw = train_test_split(X_mw, y_mw, test_size=0.2, random_state=42, stratify=y_mw)

print("Training XGBClassifier for Match Winner...")
mw_model = XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.05, random_state=42, eval_metric="logloss")
mw_model.fit(X_train_mw, y_train_mw)

y_pred_mw = mw_model.predict(X_test_mw)
y_pred_proba_mw = mw_model.predict_proba(X_test_mw)[:, 1]

mw_accuracy = accuracy_score(y_test_mw, y_pred_mw)
mw_roc_auc = roc_auc_score(y_test_mw, y_pred_proba_mw)

print(f"Match Winner Model - Accuracy: {mw_accuracy:.4f}, ROC-AUC: {mw_roc_auc:.4f}")
print("Classification Report:")
print(classification_report(y_test_mw, y_pred_mw))

with open("ml_service/models/match_winner.pkl", "wb") as f:
    pickle.dump(mw_model, f)


# ==========================================
# 2. Feature Engineering for First Innings Score Regressor
# ==========================================
print("Engineering features for First Innings Score Regressor...")
# Group deliveries by matchId and over for inning 1
first_innings_deliveries = deliveries_df[deliveries_df["inning"] == 1].copy()

# Sort by matchId, over, ball
first_innings_deliveries = first_innings_deliveries.sort_values(["matchId", "over", "ball"]).reset_index(drop=True)

# Calculate cumulative runs and wickets for each delivery
first_innings_deliveries["ball_runs"] = first_innings_deliveries["batsmanRuns"] + first_innings_deliveries["extraRuns"]
first_innings_deliveries["cum_runs"] = first_innings_deliveries.groupby("matchId")["ball_runs"].cumsum()
first_innings_deliveries["cum_wickets"] = first_innings_deliveries.groupby("matchId")["isWicket"].cumsum()

# Find final score of the first innings for each match
final_scores = first_innings_deliveries.groupby("matchId")["ball_runs"].sum().rename("final_score").reset_index()

# Find powerplay runs and wickets (at the end of over 5 / over_number <= 5 since over is 0-indexed)
powerplay_df = first_innings_deliveries[first_innings_deliveries["over"] <= 5].groupby("matchId").agg(
    powerplay_runs=("ball_runs", "sum"),
    powerplay_wickets=("isWicket", "sum")
).reset_index()

# Merge back
over_aggregated = first_innings_deliveries.groupby(["matchId", "over"]).agg(
    batting_team=("battingTeam", "first"),
    bowling_team=("bowlingTeam", "first"),
    cum_runs=("cum_runs", "last"),
    cum_wickets=("cum_wickets", "last")
).reset_index()

over_aggregated = over_aggregated.merge(final_scores, on="matchId")
over_aggregated = over_aggregated.merge(powerplay_df, on="matchId", how="left").fillna(0)
over_aggregated = over_aggregated.merge(matches_df[["matchId", "venue"]], on="matchId")

# For overs < 6, powerplay_runs and powerplay_wickets are just cumulative runs and wickets
over_aggregated["pp_runs"] = np.where(over_aggregated["over"] < 6, over_aggregated["cum_runs"], over_aggregated["powerplay_runs"])
over_aggregated["pp_wickets"] = np.where(over_aggregated["over"] < 6, over_aggregated["cum_wickets"], over_aggregated["powerplay_wickets"])

# Create score dataset
score_dataset = pd.DataFrame({
    "batting_team": over_aggregated["batting_team"].map(team_to_idx),
    "bowling_team": over_aggregated["bowling_team"].map(team_to_idx),
    "venue": over_aggregated["venue"].map(venue_to_idx),
    "powerplay_runs": over_aggregated["pp_runs"],
    "powerplay_wickets": over_aggregated["pp_wickets"],
    "over_number": over_aggregated["over"] + 1,  # Make it 1-indexed (1 to 20)
    "final_score": over_aggregated["final_score"]
}).dropna()

# Split and train LGBMRegressor
X_score = score_dataset.drop(columns=["final_score"])
y_score = score_dataset["final_score"]

X_train_score, X_test_score, y_train_score, y_test_score = train_test_split(X_score, y_score, test_size=0.2, random_state=42)

print("Training LGBMRegressor for Score Prediction...")
score_model = LGBMRegressor(n_estimators=150, max_depth=6, learning_rate=0.08, random_state=42)
score_model.fit(X_train_score, y_train_score)

y_pred_score = score_model.predict(X_test_score)
score_rmse = np.sqrt(mean_squared_error(y_test_score, y_pred_score))

print(f"Score Predictor Model - RMSE: {score_rmse:.4f}")

with open("ml_service/models/score_predictor.pkl", "wb") as f:
    pickle.dump(score_model, f)


# ==========================================
# 3. Feature Engineering for Fantasy Points Predictor
# ==========================================
print("Engineering features for Fantasy Points Predictor...")
# Construct player-match level stats
# First, calculate runs and wickets for each player in each match
player_match_batting = deliveries_df.groupby(["matchId", "batter"]).agg(
    runs=("batsmanRuns", "sum"),
    balls=("extrasType", lambda x: (x != "wides").sum()),
    fours=("batsmanRuns", lambda x: (x == 4).sum()),
    sixes=("batsmanRuns", lambda x: (x == 6).sum())
).reset_index().rename(columns={"batter": "player"})

player_match_bowling = deliveries_df.groupby(["matchId", "bowler"]).agg(
    balls_bowled=("extrasType", lambda x: ((x != "wides") & (x != "noballs")).sum()),
    runs_conceded=("extrasType", lambda x: (~x.isin(["byes", "legbyes"])).sum()),  # Wait, let's sum totalRuns for non-byes
    wickets=("isWicket", "sum") # We will filter by valid wicket kind later, but this is a match-level summary. Let's do it right.
).reset_index().rename(columns={"bowler": "player"})

# Re-calculate bowler runs conceded correctly (sum totalRuns where extrasType is not byes/legbyes)
deliveries_df["runs_for_bowler"] = np.where(~deliveries_df["extrasType"].isin(["byes", "legbyes"]), deliveries_df["totalRuns"], 0)
deliveries_df["is_bowler_wicket"] = np.where(deliveries_df["isWicket"] == 1 & deliveries_df["dismissalKind"].str.lower().isin(VALID_WICKET_KINDS), 1, 0)

player_match_bowling_clean = deliveries_df.groupby(["matchId", "bowler"]).agg(
    balls_bowled=("extrasType", lambda x: ((x != "wides") & (x != "noballs")).sum()),
    runs_conceded=("runs_for_bowler", "sum"),
    wickets=("is_bowler_wicket", "sum")
).reset_index().rename(columns={"bowler": "player"})

# Fielding points
player_match_fielding = deliveries_df.groupby(["matchId", "fielder"]).agg(
    catches=("dismissalKind", lambda x: (x.str.lower() == "caught").sum()),
    stumpings=("dismissalKind", lambda x: (x.str.lower() == "stumped").sum()),
    run_outs=("dismissalKind", lambda x: (x.str.lower() == "run out").sum())
).reset_index().rename(columns={"fielder": "player"})
player_match_fielding = player_match_fielding[player_match_fielding["player"] != "NA"]

# Merge player-match statistics
player_match_stats = player_match_batting.merge(player_match_bowling_clean, on=["matchId", "player"], how="outer").merge(
    player_match_fielding, on=["matchId", "player"], how="outer"
).fillna(0)

# Calculate Fantasy Points for each player-match
# Runs: 1, Wickets: 25, Fours: 1, Sixes: 2, Catch: 8, Stumping: 12, RunOut: 6
# 30 bonus: +4, 50 bonus: +8, 100 bonus: +16
# 3w bonus: +4, 4w bonus: +8, 5w: +16
def calculate_fantasy_points(row):
    runs = row["runs"]
    wickets = row["wickets"]
    fours = row["fours"]
    sixes = row["sixes"]
    catches = row["catches"]
    stumpings = row["stumpings"]
    run_outs = row["run_outs"]
    
    points = runs + (fours * 1) + (sixes * 2) + (wickets * 25) + (catches * 8) + (stumpings * 12) + (run_outs * 6)
    
    # Milestone bonuses
    if runs >= 100:
        points += 16
    elif runs >= 50:
        points += 8
    elif runs >= 30:
        points += 4
        
    if wickets >= 5:
        points += 16
    elif wickets >= 4:
        points += 8
    elif wickets >= 3:
        points += 4
        
    return points

player_match_stats["fantasy_points"] = player_match_stats.apply(calculate_fantasy_points, axis=1)

# Add match info
player_match_stats = player_match_stats.merge(matches_df[["matchId", "venue", "season", "date", "team1", "team2"]], on="matchId")

# Sort chronologically to compute player forms without data leakage
player_match_stats = player_match_stats.sort_values("date").reset_index(drop=True)

# Precompute opponent batting and bowling ranks per season
# Batting rank = average runs scored per over by the team in that season
# Bowling rank = average runs conceded per over by the team in that season
team_season_bat = deliveries_df.groupby(["matchId", "battingTeam"]).agg(
    runs=("totalRuns", "sum"),
    balls=("extrasType", lambda x: (x != "wides").sum())
).reset_index().merge(matches_df[["matchId", "season"]], on="matchId")

team_season_bat_agg = team_season_bat.groupby(["season", "battingTeam"]).agg(
    total_runs=("runs", "sum"),
    total_balls=("balls", "sum")
).reset_index()
team_season_bat_agg["rpo"] = team_season_bat_agg["total_runs"] / (team_season_bat_agg["total_balls"] / 6)
team_season_bat_agg["bat_rank"] = team_season_bat_agg.groupby("season")["rpo"].rank(ascending=False, method="min").astype(int)

team_season_bowl = deliveries_df.groupby(["matchId", "bowlingTeam"]).agg(
    runs_conceded=("runs_for_bowler", "sum"),
    balls_bowled=("extrasType", lambda x: ((x != "wides") & (x != "noballs")).sum())
).reset_index().merge(matches_df[["matchId", "season"]], on="matchId")

team_season_bowl_agg = team_season_bowl.groupby(["season", "bowlingTeam"]).agg(
    total_runs_conceded=("runs_conceded", "sum"),
    total_balls_bowled=("balls_bowled", "sum")
).reset_index()
team_season_bowl_agg["rpo_conceded"] = team_season_bowl_agg["total_runs_conceded"] / (team_season_bowl_agg["total_balls_bowled"] / 6)
team_season_bowl_agg["bowl_rank"] = team_season_bowl_agg.groupby("season")["rpo_conceded"].rank(ascending=True, method="min").astype(int)

# Create lookup maps
bat_rank_lookup = team_season_bat_agg.set_index(["season", "battingTeam"])["bat_rank"].to_dict()
bowl_rank_lookup = team_season_bowl_agg.set_index(["season", "bowlingTeam"])["bowl_rank"].to_dict()

# To store engineered features
fantasy_features_data = []

# Tracks historical rolling stats per player
player_history = {} # name: list of dicts {runs, wickets, balls, runs_conceded, balls_bowled, venue_points: {venue: list}}

for idx, row in player_match_stats.iterrows():
    p = row["player"]
    venue = row["venue"]
    season = row["season"]
    match_id = row["matchId"]
    t1 = row["team1"]
    t2 = row["team2"]

    # Determine opponent team
    # We need to find which team the player played against in this match.
    # To find this, we check which team the player belongs to.
    # Let's see: if the player batted, their team is battingTeam. If they bowled, bowlingTeam.
    # If not found, we can approximate based on who they played for.
    # Let's find which team this player belonged to in this match
    p_deliveries = deliveries_df[(deliveries_df["matchId"] == match_id) & 
                                 ((deliveries_df["batter"] == p) | 
                                  (deliveries_df["bowler"] == p) | 
                                  (deliveries_df["fielder"] == p))]
    if not p_deliveries.empty:
        p_team = p_deliveries.iloc[0]["battingTeam"] if p_deliveries.iloc[0]["batter"] == p else p_deliveries.iloc[0]["bowlingTeam"]
    else:
        p_team = t1 # fallback
        
    opponent_team = t2 if p_team == t1 else t1

    # Get ranks
    opp_bat_rank = bat_rank_lookup.get((season, opponent_team), 5)
    opp_bowl_rank = bowl_rank_lookup.get((season, opponent_team), 5)

    if p not in player_history:
        player_history[p] = {
            "runs": [], "wickets": [], "balls_faced": [], "runs_conceded": [], "balls_bowled": [],
            "venue_points": {}
        }

    history = player_history[p]

    # Calculate features based on history BEFORE this match
    recent_runs = history["runs"][-5:]
    recent_wickets = history["wickets"][-5:]
    recent_balls = history["balls_faced"][-5:]
    recent_runs_conceded = history["runs_conceded"][-5:]
    recent_balls_bowled = history["balls_bowled"][-5:]

    avg_runs = np.mean(recent_runs) if recent_runs else 0.0
    avg_wickets = np.mean(recent_wickets) if recent_wickets else 0.0
    
    # Strike rate in last 5 matches
    tot_runs = sum(recent_runs)
    tot_balls = sum(recent_balls)
    strike_rate = (tot_runs / tot_balls * 100) if tot_balls > 0 else 0.0

    # Economy in last 5 matches
    tot_runs_conceded = sum(recent_runs_conceded)
    tot_balls_bowled = sum(recent_balls_bowled)
    economy = (tot_runs_conceded / (tot_balls_bowled / 6)) if tot_balls_bowled > 0 else 0.0

    # Venue average points
    venue_pts = history["venue_points"].get(venue, [])
    venue_avg = np.mean(venue_pts) if venue_pts else 25.0 # default/average fantasy points

    fantasy_features_data.append({
        "player_recent_avg_runs": avg_runs,
        "player_recent_avg_wickets": avg_wickets,
        "player_strike_rate": strike_rate,
        "player_economy": economy,
        "player_at_venue_avg": venue_avg,
        "opponent_bowling_rank": opp_bowl_rank,
        "opponent_batting_rank": opp_bat_rank,
        "fantasy_points_scored": row["fantasy_points"]
    })

    # Update history with this match's results
    history["runs"].append(row["runs"])
    history["wickets"].append(row["wickets"])
    history["balls_faced"].append(row["balls"])
    history["runs_conceded"].append(row["runs_conceded"])
    history["balls_bowled"].append(row["balls_bowled"])
    if venue not in history["venue_points"]:
        history["venue_points"][venue] = []
    history["venue_points"][venue].append(row["fantasy_points"])

fantasy_df = pd.DataFrame(fantasy_features_data)

# Split and train GradientBoostingRegressor
X_fan = fantasy_df.drop(columns=["fantasy_points_scored"])
y_fan = fantasy_df["fantasy_points_scored"]

X_train_fan, X_test_fan, y_train_fan, y_test_fan = train_test_split(X_fan, y_fan, test_size=0.2, random_state=42)

print("Training GradientBoostingRegressor for Fantasy Points...")
fan_model = GradientBoostingRegressor(n_estimators=100, max_depth=5, learning_rate=0.08, random_state=42)
fan_model.fit(X_train_fan, y_train_fan)

y_pred_fan = fan_model.predict(X_test_fan)
fan_rmse = np.sqrt(mean_squared_error(y_test_fan, y_pred_fan))

print(f"Fantasy Points Predictor Model - RMSE: {fan_rmse:.4f}")

with open("ml_service/models/fantasy_points.pkl", "wb") as f:
    pickle.dump(fan_model, f)


# ==========================================
# 4. Save Metrics JSON
# ==========================================
metrics = {
    "match_winner": {
        "accuracy": float(mw_accuracy),
        "roc_auc": float(mw_roc_auc)
    },
    "score_predictor": {
        "rmse": float(score_rmse)
    },
    "fantasy_points": {
        "rmse": float(fan_rmse)
    }
}

with open("ml_service/models/metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

print("All models trained and saved successfully inside ml_service/models/!")
client.close()
