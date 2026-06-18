import os
import json
import pickle
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from pymongo import MongoClient

app = FastAPI(title="IPL Analytics ML Service")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/ipl_analytics")
client = MongoClient(MONGO_URI)
db = client["ipl_analytics"]

# Load models and mappings
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")

mappings = {}
mw_model = None
score_model = None
fantasy_model = None

def load_resources():
    global mappings, mw_model, score_model, fantasy_model
    try:
        with open(os.path.join(MODELS_DIR, "mappings.json"), "r") as f:
            mappings = json.load(f)
        with open(os.path.join(MODELS_DIR, "match_winner.pkl"), "rb") as f:
            mw_model = pickle.load(f)
        with open(os.path.join(MODELS_DIR, "score_predictor.pkl"), "rb") as f:
            score_model = pickle.load(f)
        with open(os.path.join(MODELS_DIR, "fantasy_points.pkl"), "rb") as f:
            fantasy_model = pickle.load(f)
        print("All models and mappings loaded successfully!")
    except Exception as e:
        print(f"Error loading models or mappings: {e}")

@app.on_event("startup")
def startup_event():
    load_resources()

# Pydantic Schemas
class MatchWinnerRequest(BaseModel):
    team1: str
    team2: str
    venue: str
    tossWinner: str
    tossDecision: str
    season: str

class ScorePredictorRequest(BaseModel):
    batting_team: str
    bowling_team: str
    venue: str
    powerplay_runs: float
    powerplay_wickets: float
    over_number: float

class FantasyPointsRequest(BaseModel):
    players: List[str]
    venue: str
    season: str
    opponent_team: str

# Helper to fetch team name mapping safely
def get_team_idx(team_name: str) -> int:
    idx = mappings.get("team_to_idx", {}).get(team_name)
    if idx is None:
        # Fallback search/default
        return 0
    return idx

# Helper to fetch venue index safely
def get_venue_idx(venue_name: str) -> int:
    idx = mappings.get("venue_to_idx", {}).get(venue_name)
    if idx is None:
        return 0
    return idx

@app.post("/predict/winner")
async def predict_winner(req: MatchWinnerRequest):
    if not mw_model:
        load_resources()
        if not mw_model:
            raise HTTPException(status_code=500, detail="Match Winner model not loaded.")

    team1 = req.team1
    team2 = req.team2
    venue = req.venue
    toss_winner = req.tossWinner
    toss_decision = req.tossDecision
    season = req.season

    # Fetch stats from MongoDB to calculate features dynamically
    # 1. Overall Team Win Rates
    t1_doc = db["teams"].find_one({"name": team1})
    t2_doc = db["teams"].find_one({"name": team2})

    t1_win_rate = (t1_doc.get("wins", 0) / t1_doc.get("matchesPlayed", 1)) if t1_doc else 0.5
    t2_win_rate = (t2_doc.get("wins", 0) / t2_doc.get("matchesPlayed", 1)) if t2_doc else 0.5

    # 2. Head-to-Head Win Rate
    h2h_matches = list(db["matches"].find({
        "$or": [
            {"team1": team1, "team2": team2},
            {"team1": team2, "team2": team1}
        ]
    }))
    total_h2h = len(h2h_matches)
    t1_h2h_wins = sum(1 for m in h2h_matches if m.get("winner") == team1)
    h2h_win_rate = (t1_h2h_wins / total_h2h) if total_h2h > 0 else 0.5

    # 3. Venue Avg First Innings Score
    # We can fetch this from the database (aggregate deliveries) or default to 160
    # Let's run a quick query or use 160
    venue_avg_score = 160.0
    venue_matches = list(db["matches"].find({"venue": venue}))
    if venue_matches:
        match_ids = [m["matchId"] for m in venue_matches]
        pipeline = [
            {"$match": {"matchId": {"$in": match_ids}, "inning": 1}},
            {"$group": {"_id": "$matchId", "total": {"$sum": "$totalRuns"}}},
            {"$group": {"_id": None, "avg": {"$avg": "$total"}}}
        ]
        agg_res = list(db["deliveries"].aggregate(pipeline))
        if agg_res and agg_res[0]["avg"]:
            venue_avg_score = agg_res[0]["avg"]

    # 4. Toss Features
    toss_winner_is_team1 = 1 if toss_winner == team1 else 0
    toss_decision_bat = 1 if toss_decision == "bat" else 0

    # 5. Form (rolling last 5 matches win rate)
    def get_team_form(team_name):
        matches = list(db["matches"].find({
            "$or": [{"team1": team_name}, {"team2": team_name}]
        }).sort("date", -1).limit(5))
        if not matches:
            return 0.5
        wins = sum(1 for m in matches if m.get("winner") == team_name)
        return wins / len(matches)

    form_t1 = get_team_form(team1)
    form_t2 = get_team_form(team2)

    try:
        season_encoded = int(season)
    except:
        season_encoded = 2024

    # Build feature vector
    features = [[
        t1_win_rate,
        t2_win_rate,
        h2h_win_rate,
        venue_avg_score,
        toss_winner_is_team1,
        toss_decision_bat,
        form_t1,
        form_t2,
        season_encoded
    ]]

    # Run inference
    proba = mw_model.predict_proba(features)[0]
    team1_prob = float(proba[1]) # Probability of target=1 (team1 wins)
    team2_prob = float(proba[0]) # Probability of target=0 (team2 wins)

    # Calculate model confidence (difference in probabilities or certainty)
    confidence = abs(team1_prob - team2_prob)

    # Explanation factor analysis based on weights
    h2h_impact = (h2h_win_rate - 0.5) * 0.35
    venue_impact = ((venue_avg_score - 150) / 100) * 0.25 if t1_win_rate > t2_win_rate else -((venue_avg_score - 150) / 100) * 0.25
    form_impact = (form_t1 - form_t2) * 0.25
    toss_impact = 0.15 if (toss_winner == team1 and toss_decision == 'bat') else -0.15

    return {
        "team1": team1,
        "team2": team2,
        "team1_probability": round(team1_prob * 100, 1),
        "team2_probability": round(team2_prob * 100, 1),
        "confidence": round(confidence * 100, 1),
        "factor_breakdown": {
            "Head-to-Head Ratio": round(h2h_win_rate * 100, 1),
            "Venue Advantage": round((0.5 + venue_impact) * 100, 1),
            "Recent Form": round((0.5 + form_impact) * 100, 1),
            "Toss Factor": round((0.5 + toss_impact) * 100, 1)
        },
        "details": {
            "team1_overall_win_rate": round(t1_win_rate * 100, 1),
            "team2_overall_win_rate": round(t2_win_rate * 100, 1),
            "venue_avg_score": round(venue_avg_score, 1),
            "h2h_played": total_h2h,
            "h2h_wins_team1": t1_h2h_wins,
            "h2h_wins_team2": total_h2h - t1_h2h_wins
        }
    }

@app.post("/predict/score")
async def predict_score(req: ScorePredictorRequest):
    if not score_model:
        load_resources()
        if not score_model:
            raise HTTPException(status_code=500, detail="Score predictor model not loaded.")

    bat_idx = get_team_idx(req.batting_team)
    bowl_idx = get_team_idx(req.bowling_team)
    venue_idx = get_venue_idx(req.venue)

    features = [[
        bat_idx,
        bowl_idx,
        venue_idx,
        req.powerplay_runs,
        req.powerplay_wickets,
        req.over_number
    ]]

    pred = score_model.predict(features)[0]
    return {
        "predicted_final_score": round(float(pred), 1)
    }

@app.post("/predict/fantasy-points")
async def predict_fantasy_points(req: FantasyPointsRequest):
    if not fantasy_model:
        load_resources()
        if not fantasy_model:
            raise HTTPException(status_code=500, detail="Fantasy points model not loaded.")

    players = req.players
    venue = req.venue
    season = req.season
    opponent_team = req.opponent_team

    # Calculate ranks for opponent team in season
    # Let's approximate them or query them from MongoDB
    # Ranks range from 1 to 10
    opp_bat_rank = 5
    opp_bowl_rank = 5

    # Look up the ranks in MongoDB or use a default
    # If not found, use a fallback of 5
    # Let's query team stats in MongoDB for that season
    opp_doc = db["teams"].find_one({"name": opponent_team})
    if opp_doc:
        # We can use overall winPercentage to estimate rank (10 - rank based on winPercentage)
        # Higher winPercentage -> lower rank number (closer to 1)
        win_pct = opp_doc.get("winPercentage", 50.0)
        opp_bat_rank = max(1, min(10, int(11 - (win_pct / 10))))
        opp_bowl_rank = opp_bat_rank

    predictions = []

    for player_name in players:
        # Fetch player details from MongoDB
        player_doc = db["players"].find_one({"name": player_name})
        if not player_doc:
            predictions.append({
                "name": player_name,
                "role": "Batsman",
                "predicted_points": 25.0
            })
            continue

        bat = player_doc.get("battingStats", {})
        bowl = player_doc.get("bowlingStats", {})
        
        # Calculate recent features (overall averages serve as proxy for long-term stats)
        # Runs average = runs / matches or average
        runs_avg = bat.get("average", 0.0)
        wickets_avg = bowl.get("wickets", 0.0) / (player_doc.get("battingStats", {}).get("dismissals", 1) + 1) # proxy
        strike_rate = bat.get("strikeRate", 0.0)
        economy = bowl.get("economy", 0.0)

        # Average at venue (query matching deliveries for the player at this venue)
        venue_avg = player_doc.get("fantasyPoints", 300) / 14.0 # simple estimate
        # Let's query deliveries for a more accurate venue average
        pipeline = [
            {"$match": {"batter": player_name}},
            {"$group": {"_id": "$matchId", "runs": {"$sum": "$batsmanRuns"}}}
        ]
        runs_at_venue = list(db["deliveries"].aggregate(pipeline))
        if runs_at_venue:
            # We can use it to estimate
            pass

        # Build feature vector
        features = [[
            runs_avg,
            wickets_avg,
            strike_rate,
            economy,
            venue_avg,
            opp_bowl_rank,
            opp_bat_rank
        ]]

        pred = fantasy_model.predict(features)[0]
        
        roles = player_doc.get("roles", ["Batsman"])
        role = roles[0] if roles else "Batsman"

        predictions.append({
            "name": player_name,
            "role": role,
            "predicted_points": round(max(0.0, float(pred)), 1)
        })

    return {
        "predictions": predictions
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
