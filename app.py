import os
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="IPL Pro Analytics & Prediction Console",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Paths Configuration
DATA_DIR = os.path.join(os.path.dirname(__file__), "dataset")
MATCHES_FILE = os.path.join(DATA_DIR, "matches.csv")
DELIVERIES_FILE = os.path.join(DATA_DIR, "deliveries.csv")

# 3. CSS Injections for Premium Dark Sporty Theme
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        /* Base styles */
        html, body, [class*="css"], .stApp {
            font-family: 'Outfit', sans-serif !important;
            background-color: #0b0f19 !important;
            color: #f1f5f9 !important;
        }
        
        /* Reduce block container margins for high-end feel */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
            padding-left: 2.5rem !important;
            padding-right: 2.5rem !important;
        }
        
        /* Style native Streamlit container with borders to look like Glassmorphic Cards */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(15, 23, 42, 0.65) !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-radius: 20px !important;
            padding: 24px !important;
            margin-bottom: 24px !important;
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: rgba(56, 189, 248, 0.25) !important;
            box-shadow: 0 12px 40px rgba(56, 189, 248, 0.05) !important;
        }
        
        /* Metric cards custom styling */
        [data-testid="metric-container"] {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            padding: 18px 20px !important;
            border-radius: 16px !important;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        [data-testid="metric-container"]:hover {
            transform: translateY(-3px);
            border-color: rgba(56, 189, 248, 0.35) !important;
            box-shadow: 0 10px 30px rgba(56, 189, 248, 0.1) !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 2.3rem !important;
            font-weight: 800 !important;
            color: #38bdf8 !important;
            background: linear-gradient(135deg, #38bdf8 0%, #3b82f6 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            color: #94a3b8 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
        }
        
        /* Headers and Typography */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 800 !important;
            color: #ffffff !important;
            letter-spacing: -0.02em !important;
        }
        
        /* Custom Header container to separate sections professionally */
        .header-container {
            display: flex;
            flex-direction: column;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.07);
        }
        .dashboard-header {
            font-size: 2.4rem;
            font-weight: 800;
            margin: 0;
            line-height: 1.2;
            background: linear-gradient(135deg, #38bdf8 0%, #3b82f6 50%, #f97316 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .dashboard-subheader {
            color: #94a3b8;
            font-size: 1rem;
            font-weight: 400;
            margin-top: 6px;
            margin-bottom: 0;
        }
        .header-accent-line {
            height: 3px;
            width: 70px;
            background: linear-gradient(90deg, #38bdf8, #3b82f6);
            border-radius: 9999px;
            margin-top: 10px;
        }
        
        /* Custom KPI Card design */
        .custom-kpi-card {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.45) 0%, rgba(15, 23, 42, 0.45) 100%) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-radius: 16px !important;
            padding: 20px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25) !important;
            backdrop-filter: blur(8px) !important;
            -webkit-backdrop-filter: blur(8px) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        .custom-kpi-card:hover {
            transform: translateY(-2px);
            border-color: rgba(56, 189, 248, 0.3) !important;
            box-shadow: 0 12px 30px rgba(56, 189, 248, 0.08) !important;
        }
        
        /* Match Predictor Card */
        .predictor-container {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
            margin-bottom: 25px;
        }
        .probability-bar-container {
            width: 100%;
            background-color: #1e293b;
            border-radius: 9999px;
            height: 32px;
            overflow: hidden;
            display: flex;
            margin: 20px 0;
            border: 1px solid rgba(255,255,255,0.05);
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.6);
        }
        .prob-team-a {
            background: linear-gradient(90deg, #3b82f6 0%, #06b6d4 100%);
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 800;
            font-size: 0.95rem;
            transition: width 0.8s ease-in-out;
            text-shadow: 0 1px 2px rgba(0,0,0,0.5);
        }
        .prob-team-b {
            background: linear-gradient(90deg, #f97316 0%, #facc15 100%);
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 800;
            font-size: 0.95rem;
            transition: width 0.8s ease-in-out;
            text-shadow: 0 1px 2px rgba(0,0,0,0.5);
        }
        
        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #070a13 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        }
        /* Custom side headings */
        .sidebar-section-title {
            font-size: 0.8rem;
            font-weight: 800;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-top: 15px;
            margin-bottom: 8px;
        }
        
        /* Highlight Labels */
        .highlight-blue { color: #38bdf8; font-weight: bold; }
        .highlight-orange { color: #fb923c; font-weight: bold; }
        .highlight-gold { color: #facc15; font-weight: bold; }
        
        /* Style Streamlit Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: #0f172a !important;
            padding: 8px;
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,0.06);
            margin-bottom: 20px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 44px;
            background-color: transparent;
            border-radius: 10px;
            color: #94a3b8;
            font-weight: 600;
            padding: 0 20px;
            transition: all 0.2s ease;
            border: none !important;
        }
        .stTabs [data-baseweb="tab"]:hover {
            color: #f1f5f9;
            background-color: rgba(255, 255, 255, 0.04);
        }
        .stTabs [aria-selected="true"] {
            background-color: #1e293b !important;
            color: #38bdf8 !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        /* Lineup Board Styles */
        .lineup-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 16px;
            margin-top: 15px;
        }
        .player-badge {
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 15px;
            text-align: center;
            transition: all 0.2s ease;
        }
        .player-badge:hover {
            border-color: #38bdf8;
            transform: translateY(-2px);
        }
        .role-wk { border-left: 4px solid #facc15; }
        .role-bat { border-left: 4px solid #3b82f6; }
        .role-ar { border-left: 4px solid #a855f7; }
        .role-bowl { border-left: 4px solid #10b981; }
        
        .role-tag {
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            padding: 2px 6px;
            border-radius: 4px;
            margin-top: 5px;
            display: inline-block;
        }
        .tag-wk { background-color: rgba(250, 204, 21, 0.15); color: #facc15; }
        .tag-bat { background-color: rgba(59, 130, 246, 0.15); color: #3b82f6; }
        .tag-ar { background-color: rgba(168, 85, 247, 0.15); color: #a855f7; }
        .tag-bowl { background-color: rgba(16, 185, 129, 0.15); color: #10b981; }
    </style>
    """,
    unsafe_allow_html=True,
)

# 4. Valid Dismissal Kinds Definitions
VALID_WICKET_KINDS = {
    "bowled",
    "caught",
    "lbw",
    "stumped",
    "caught and bowled",
    "hit wicket",
}

# 5. Famous Wicketkeepers definition for Fantasy Builder
FAMOUS_WKS = {
    "ms dhoni", "kd arthik", "ab de villiers", "rr pant", "kl rahul", "sv samson",
    "q de kock", "jc buttler", "wp saha", "ac gilchrist", "kc sangakkara",
    "rv uthappa", "pa patel", "dinesh karthik", "rishabh pant", "sanju samson",
    "quinton de kock", "jos buttler", "wriddhiman saha", "kumar sangakkara",
    "robin uthappa", "parthiv patel", "ishan kishan", "lh ferguson",
    "n pooran", "nicholas pooran", "ks bharat", "j bairstow", "jonny bairstow"
}

# 6. Global Helper Functions
def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]
    return df

def _first_existing_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    for column in candidates:
        if column in df.columns:
            return column
    return None

def _numeric_or_zero_series(df: pd.DataFrame, column: str) -> pd.Series:
    if column in df.columns:
        return pd.to_numeric(df[column], errors="coerce").fillna(0)
    return pd.Series(0, index=df.index)

def update_plotly_layout(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#cbd5e1',
        font_family='Outfit',
        title_font_color='#ffffff',
        title_font_family='Outfit',
        legend_title_font_color='#94a3b8',
        margin=dict(t=50, b=30, l=30, r=30),
        xaxis=dict(
            gridcolor='rgba(255, 255, 255, 0.05)',
            zerolinecolor='rgba(255, 255, 255, 0.08)',
            linecolor='rgba(255, 255, 255, 0.08)'
        ),
        yaxis=dict(
            gridcolor='rgba(255, 255, 255, 0.05)',
            zerolinecolor='rgba(255, 255, 255, 0.08)',
            linecolor='rgba(255, 255, 255, 0.08)'
        ),
        colorway=['#3b82f6', '#f97316', '#10b981', '#a855f7', '#06b6d4', '#eab308']
    )
    return fig

# 7. Loading and Cleaning Data
@st.cache_data(show_spinner=False)
def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    matches = pd.read_csv(MATCHES_FILE)
    deliveries = pd.read_csv(DELIVERIES_FILE)
    
    matches = _normalize_columns(matches)
    deliveries = _normalize_columns(deliveries)
    
    # Calculate extra runs helper if needed
    if "wide_runs" not in deliveries.columns and "extras_type" in deliveries.columns and "extra_runs" in deliveries.columns:
        deliveries["wide_runs"] = np.where(deliveries["extras_type"] == "wides", deliveries["extra_runs"], 0)
    if "noball_runs" not in deliveries.columns and "extras_type" in deliveries.columns and "extra_runs" in deliveries.columns:
        deliveries["noball_runs"] = np.where(deliveries["extras_type"] == "noballs", deliveries["extra_runs"], 0)
        
    return matches, deliveries

def clean_matches(matches: pd.DataFrame) -> pd.DataFrame:
    matches = matches.copy()
    if "date" in matches.columns:
        matches["date"] = pd.to_datetime(matches["date"], errors="coerce")
    if "season" in matches.columns:
        matches["season"] = matches["season"].astype(str).str.split('/').str[0]
        matches["season"] = pd.to_numeric(matches["season"], errors="coerce").astype("Int64")

    categorical_columns = [
        col for col in [
            "city", "venue", "team1", "team2", "toss_winner", "toss_decision", "winner", "result", "player_of_match"
        ] if col in matches.columns
    ]
    for col in categorical_columns:
        matches[col] = matches[col].fillna("Unknown")

    numeric_columns = [col for col in ["win_by_runs", "win_by_wickets", "dl_applied"] if col in matches.columns]
    for col in numeric_columns:
        matches[col] = pd.to_numeric(matches[col], errors="coerce").fillna(0)

    matches = matches.drop_duplicates().reset_index(drop=True)
    return matches

def clean_deliveries(deliveries: pd.DataFrame) -> pd.DataFrame:
    deliveries = deliveries.copy()
    for col in deliveries.columns:
        if deliveries[col].dtype == object:
            deliveries[col] = deliveries[col].fillna("Unknown")
            
    numeric_cols = [
        "match_id", "inning", "over", "ball", "batsman_runs", "total_runs", 
        "wide_runs", "bye_runs", "legbye_runs", "noball_runs", "penalty_runs", 
        "extra_runs", "is_super_over"
    ]
    for col in numeric_cols:
        if col in deliveries.columns:
            deliveries[col] = pd.to_numeric(deliveries[col], errors="coerce").fillna(0)
            
    deliveries = deliveries.drop_duplicates().reset_index(drop=True)
    return deliveries

def prepare_data(matches: pd.DataFrame, deliveries: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    matches = clean_matches(matches)
    deliveries = clean_deliveries(deliveries)

    match_id_col = _first_existing_column(matches, ["id", "match_id"])
    delivery_match_col = _first_existing_column(deliveries, ["match_id", "id"])

    if match_id_col and delivery_match_col and match_id_col != delivery_match_col:
        deliveries = deliveries.rename(columns={delivery_match_col: match_id_col})
        delivery_match_col = match_id_col

    if match_id_col and delivery_match_col and match_id_col in matches.columns and delivery_match_col in deliveries.columns:
        merged = deliveries.merge(matches, on=match_id_col, how="left", suffixes=("", "_match"))
    else:
        merged = deliveries.copy()

    return {"matches": matches, "deliveries": deliveries, "merged": merged}

# 8. Filtration pools helpers
def get_team_pool(matches: pd.DataFrame) -> List[str]:
    team_columns = [col for col in ["team1", "team2", "winner", "toss_winner"] if col in matches.columns]
    teams = set()
    for col in team_columns:
        teams.update(matches[col].dropna().astype(str).unique().tolist())
    teams.discard("Unknown")
    return sorted(teams)

def get_season_pool(matches: pd.DataFrame) -> List[int]:
    if "season" not in matches.columns:
        return []
    seasons = matches["season"].dropna().astype(int).unique().tolist()
    return sorted(seasons)

def filter_matches(matches: pd.DataFrame, selected_seasons: List[int], selected_team: str) -> pd.DataFrame:
    filtered = matches.copy()
    if selected_seasons and "season" in filtered.columns:
        filtered = filtered[filtered["season"].isin(selected_seasons)]
    if selected_team != "All Teams":
        team_mask = pd.Series(False, index=filtered.index)
        for col in ["team1", "team2", "winner", "toss_winner"]:
            if col in filtered.columns:
                team_mask = team_mask | (filtered[col] == selected_team)
        filtered = filtered[team_mask]
    return filtered

def filter_deliveries(deliveries: pd.DataFrame, matches: pd.DataFrame) -> pd.DataFrame:
    match_id_col = _first_existing_column(matches, ["id", "match_id"])
    delivery_match_col = _first_existing_column(deliveries, ["match_id", "id"])
    if match_id_col and delivery_match_col and match_id_col in matches.columns and delivery_match_col in deliveries.columns:
        valid_ids = matches[match_id_col].dropna().unique()
        return deliveries[deliveries[delivery_match_col].isin(valid_ids)].copy()
    return deliveries.copy()

# 9. Match Prediction Calculations
def compute_match_prediction(matches: pd.DataFrame, team_a: str, team_b: str, venue: str, toss_winner: str, toss_decision: str) -> Dict:
    matches_played_a = len(matches[(matches['team1'] == team_a) | (matches['team2'] == team_a)])
    matches_played_b = len(matches[(matches['team1'] == team_b) | (matches['team2'] == team_b)])
    
    wins_a = len(matches[matches['winner'] == team_a])
    wins_b = len(matches[matches['winner'] == team_b])
    
    win_rate_a = (wins_a / matches_played_a) if matches_played_a > 0 else 0.5
    win_rate_b = (wins_b / matches_played_b) if matches_played_b > 0 else 0.5
    
    h2h_matches = matches[((matches['team1'] == team_a) & (matches['team2'] == team_b)) | 
                          ((matches['team1'] == team_b) & (matches['team2'] == team_a))]
    total_h2h = len(h2h_matches)
    
    if total_h2h > 0:
        h2h_wins_a = len(h2h_matches[h2h_matches['winner'] == team_a])
        h2h_wins_b = len(h2h_matches[h2h_matches['winner'] == team_b])
        h2h_factor_a = (h2h_wins_a + 1) / (total_h2h + 2)
    else:
        h2h_factor_a = win_rate_a / (win_rate_a + win_rate_b) if (win_rate_a + win_rate_b) > 0 else 0.5
        h2h_wins_a = 0
        h2h_wins_b = 0
        
    venue_matches_a = matches[((matches['team1'] == team_a) | (matches['team2'] == team_a)) & (matches['venue'] == venue)]
    venue_matches_b = matches[((matches['team1'] == team_b) | (matches['team2'] == team_b)) & (matches['venue'] == venue)]
    
    venue_win_rate_a = (len(venue_matches_a[venue_matches_a['winner'] == team_a]) / len(venue_matches_a)) if len(venue_matches_a) > 0 else win_rate_a
    venue_win_rate_b = (len(venue_matches_b[venue_matches_b['winner'] == team_b]) / len(venue_matches_b)) if len(venue_matches_b) > 0 else win_rate_b
    
    wt_a = min(len(venue_matches_a) / 5.0, 1.0)
    wt_b = min(len(venue_matches_b) / 5.0, 1.0)
    
    final_venue_win_rate_a = (wt_a * venue_win_rate_a) + ((1 - wt_a) * win_rate_a)
    final_venue_win_rate_b = (wt_b * venue_win_rate_b) + ((1 - wt_b) * win_rate_b)
    
    venue_factor_a = final_venue_win_rate_a / (final_venue_win_rate_a + final_venue_win_rate_b) if (final_venue_win_rate_a + final_venue_win_rate_b) > 0 else 0.5
    
    recent_a = matches[(matches['team1'] == team_a) | (matches['team2'] == team_a)].sort_values('date', ascending=False).head(8)
    recent_b = matches[(matches['team1'] == team_b) | (matches['team2'] == team_b)].sort_values('date', ascending=False).head(8)
    
    form_wins_a = len(recent_a[recent_a['winner'] == team_a])
    form_wins_b = len(recent_b[recent_b['winner'] == team_b])
    
    form_rate_a = (form_wins_a / len(recent_a)) if len(recent_a) > 0 else 0.5
    form_rate_b = (form_wins_b / len(recent_b)) if len(recent_b) > 0 else 0.5
    
    form_factor_a = form_rate_a / (form_rate_a + form_rate_b) if (form_rate_a + form_rate_b) > 0 else 0.5
    
    if toss_winner == team_a:
        bat_first_team = team_a if toss_decision == 'bat' else team_b
    else:
        bat_first_team = team_b if toss_decision == 'bat' else team_a
        
    venue_all = matches[matches['venue'] == venue]
    if len(venue_all) > 3:
        if 'win_by_runs' in venue_all.columns:
            bat_first_wins = len(venue_all[venue_all['win_by_runs'] > 0])
            chasing_wins = len(venue_all[venue_all['win_by_wickets'] > 0])
        elif 'result' in venue_all.columns:
            bat_first_wins = len(venue_all[venue_all['result'].astype(str).str.lower() == 'runs'])
            chasing_wins = len(venue_all[venue_all['result'].astype(str).str.lower() == 'wickets'])
        else:
            bat_first_wins, chasing_wins = 1, 1
            
        total_results = bat_first_wins + chasing_wins
        bat_first_rate = (bat_first_wins / total_results) if total_results > 0 else 0.48
    else:
        bat_first_rate = 0.48
        
    toss_factor_a = bat_first_rate if bat_first_team == team_a else (1.0 - bat_first_rate)
    
    prob_a_raw = (0.35 * h2h_factor_a) + (0.25 * venue_factor_a) + (0.25 * form_factor_a) + (0.15 * toss_factor_a)
    prob_a = max(min(prob_a_raw, 0.95), 0.05)
    prob_b = 1.0 - prob_a
    
    return {
        'team_a_prob': round(prob_a * 100, 1),
        'team_b_prob': round(prob_b * 100, 1),
        'h2h_factor': round(h2h_factor_a * 100, 1),
        'venue_factor': round(venue_factor_a * 100, 1),
        'form_factor': round(form_factor_a * 100, 1),
        'toss_factor': round(toss_factor_a * 100, 1),
        'total_h2h': total_h2h,
        'h2h_wins_a': h2h_wins_a,
        'h2h_wins_b': h2h_wins_b,
        'venue_matches_a': len(venue_matches_a),
        'venue_matches_b': len(venue_matches_b),
        'form_wins_a': form_wins_a,
        'form_wins_b': form_wins_b
    }

# 10. Direct Batsman vs Bowler Matchup Query
def compute_player_matchup(deliveries: pd.DataFrame, batsman: str, bowler: str) -> Dict:
    matchup_df = deliveries[(deliveries['batter'] == batsman) & (deliveries['bowler'] == bowler)]
    if matchup_df.empty:
        return {}
        
    runs_scored = matchup_df['batsman_runs'].sum()
    balls_faced = len(matchup_df[matchup_df['extras_type'] != 'wides'])
    
    dismissals = len(matchup_df[(matchup_df['player_dismissed'] == batsman) & 
                                (matchup_df['dismissal_kind'].str.lower().isin(VALID_WICKET_KINDS))])
    
    fours = len(matchup_df[matchup_df['batsman_runs'] == 4])
    sixes = len(matchup_df[matchup_df['batsman_runs'] == 6])
    dots = len(matchup_df[(matchup_df['batsman_runs'] == 0) & (matchup_df['extra_runs'] == 0)])
    
    strike_rate = (runs_scored / balls_faced * 100) if balls_faced > 0 else 0.0
    
    return {
        'runs': int(runs_scored),
        'balls': int(balls_faced),
        'dismissals': int(dismissals),
        'fours': int(fours),
        'sixes': int(sixes),
        'dots': int(dots),
        'strike_rate': round(strike_rate, 2)
    }

# 11. Smart Fantasy XI Selector Algo
def build_fantasy_xi(deliveries: pd.DataFrame, strategy: str = "Balanced XI") -> List[Dict]:
    if deliveries.empty:
        return []
        
    batsman_col = _first_existing_column(deliveries, ["batsman", "striker", "batter"])
    bowler_col = _first_existing_column(deliveries, ["bowler"])
    delivery_match_col = _first_existing_column(deliveries, ["match_id", "id"])
    
    if not batsman_col or not bowler_col:
        return []
        
    legal_bat = deliveries[deliveries['extras_type'] != 'wides']
    bat_agg = {
        'runs': ('batsman_runs', 'sum'),
        'balls': ('batsman_runs', 'count'),
    }
    if delivery_match_col and delivery_match_col in legal_bat.columns:
        bat_agg['matches'] = (delivery_match_col, 'nunique')
    bat_stats = legal_bat.groupby(batsman_col).agg(**bat_agg).reset_index().rename(columns={batsman_col: 'player'})
    if 'matches' not in bat_stats.columns:
        bat_stats['matches'] = 1
    
    fours = deliveries[deliveries['batsman_runs'] == 4].groupby(batsman_col).size().reset_index(name='fours').rename(columns={batsman_col: 'player'})
    sixes = deliveries[deliveries['batsman_runs'] == 6].groupby(batsman_col).size().reset_index(name='sixes').rename(columns={batsman_col: 'player'})
    
    bat_stats = bat_stats.merge(fours, on='player', how='left').merge(sixes, on='player', how='left').fillna(0)
    bat_stats['strike_rate'] = np.where(bat_stats['balls'] > 0, (bat_stats['runs'] / bat_stats['balls'] * 100).round(2), 0.0)
    
    wicket_mask = deliveries['dismissal_kind'].str.lower().isin(VALID_WICKET_KINDS)
    bowler_wickets = deliveries[wicket_mask].groupby(bowler_col).size().reset_index(name='wickets')
    
    legal_balls_bowled = deliveries[(deliveries['extras_type'] != 'wides') & (deliveries['extras_type'] != 'noballs')]
    bowler_balls = legal_balls_bowled.groupby(bowler_col).size().reset_index(name='balls_bowled')
    
    bowler_runs = deliveries[~deliveries['extras_type'].isin(['byes', 'legbyes'])].groupby(bowler_col)['total_runs'].sum().reset_index(name='runs_conceded')
    
    bowl_stats = bowler_balls.merge(bowler_wickets, on=bowler_col, how='left').merge(bowler_runs, on=bowler_col, how='left').fillna(0)
    bowl_stats = bowl_stats.rename(columns={bowler_col: 'player'})
    bowl_stats['overs_bowled'] = (bowl_stats['balls_bowled'] / 6).round(1)
    bowl_stats['economy'] = np.where(bowl_stats['overs_bowled'] > 0, (bowl_stats['runs_conceded'] / bowl_stats['overs_bowled']).round(2), 0.0)
    
    players_df = pd.merge(bat_stats, bowl_stats, on='player', how='outer').fillna(0)
    
    roles = []
    for idx, row in players_df.iterrows():
        p_name = row['player'].lower()
        runs = row['runs']
        wickets = row['wickets']
        
        if p_name in FAMOUS_WKS:
            roles.append('Wicketkeeper')
        elif runs >= 150 and wickets >= 5:
            roles.append('All-Rounder')
        elif wickets >= 6 and (runs < 100 or wickets * 22 > runs):
            roles.append('Bowler')
        else:
            roles.append('Batsman')
            
    players_df['role'] = roles
    
    scores = []
    for idx, row in players_df.iterrows():
        role = row['role']
        runs = row['runs']
        sr = row['strike_rate']
        w = row['wickets']
        econ = row['economy']
        matches = max(float(row.get('matches', 1)), 1)
        
        bat_points = (runs / matches) * 2 + (sr / 15) + (row['fours'] * 0.5) + (row['sixes'] * 1.5)
        bowl_points = (w / matches) * 35 + (20 - econ) * 2 if w > 0 else 0.0
        
        if strategy == "Batting-Heavy XI":
            bat_points *= 1.4
            bowl_points *= 0.8
        elif strategy == "Bowling-Heavy XI":
            bat_points *= 0.8
            bowl_points *= 1.4
            
        if role == 'Wicketkeeper':
            scores.append(bat_points + 5)
        elif role == 'Batsman':
            scores.append(bat_points)
        elif role == 'Bowler':
            scores.append(bowl_points)
        else:
            scores.append(bat_points + bowl_points)
            
    players_df['fantasy_score'] = scores
    
    wk_pool = players_df[players_df['role'] == 'Wicketkeeper'].sort_values('fantasy_score', ascending=False)
    bat_pool = players_df[players_df['role'] == 'Batsman'].sort_values('fantasy_score', ascending=False)
    ar_pool = players_df[players_df['role'] == 'All-Rounder'].sort_values('fantasy_score', ascending=False)
    bowl_pool = players_df[players_df['role'] == 'Bowler'].sort_values('fantasy_score', ascending=False)
    
    selected = []
    
    if not wk_pool.empty:
        selected.append(wk_pool.iloc[0].to_dict())
    else:
        top_fallback = players_df.sort_values('fantasy_score', ascending=False).iloc[0].to_dict()
        top_fallback['role'] = 'Wicketkeeper'
        selected.append(top_fallback)
        
    selected_names = {x['player'] for x in selected}
    
    if strategy == "Batting-Heavy XI":
        bat_count, ar_count, bowl_count = 5, 2, 3
    elif strategy == "Bowling-Heavy XI":
        bat_count, ar_count, bowl_count = 3, 2, 5
    else: # Balanced
        bat_count, ar_count, bowl_count = 4, 2, 4
        
    added = 0
    for idx, row in bat_pool.iterrows():
        if row['player'] not in selected_names and added < bat_count:
            selected.append(row.to_dict())
            selected_names.add(row['player'])
            added += 1
            
    added = 0
    for idx, row in ar_pool.iterrows():
        if row['player'] not in selected_names and added < ar_count:
            selected.append(row.to_dict())
            selected_names.add(row['player'])
            added += 1
            
    added = 0
    for idx, row in bowl_pool.iterrows():
        if row['player'] not in selected_names and added < bowl_count:
            selected.append(row.to_dict())
            selected_names.add(row['player'])
            added += 1
            
    overall_sorted = players_df.sort_values('fantasy_score', ascending=False)
    for idx, row in overall_sorted.iterrows():
        if len(selected) >= 11:
            break
        if row['player'] not in selected_names:
            selected.append(row.to_dict())
            selected_names.add(row['player'])
            
    selected_sorted = sorted(selected, key=lambda x: x['fantasy_score'], reverse=True)
    for i, player in enumerate(selected_sorted):
        if i == 0:
            player['role_detail'] = "Captain (C)"
        elif i == 1:
            player['role_detail'] = "Vice Captain (VC)"
        else:
            player['role_detail'] = "Player"
            
    return selected_sorted

# 12. View Rendering Functions
def render_team_metrics(matches: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    if matches.empty:
        return {"wins": pd.DataFrame(), "win_pct": pd.DataFrame(), "toss": pd.DataFrame(), "bat_chase": pd.DataFrame()}

    total_matches = pd.concat([matches["team1"], matches["team2"]]).dropna()
    matches_played = total_matches.value_counts().rename_axis("team").reset_index(name="matches_played")

    wins = matches["winner"].dropna().value_counts().rename_axis("team").reset_index(name="wins")
    team_summary = matches_played.merge(wins, on="team", how="left").fillna(0)
    team_summary["wins"] = team_summary["wins"].astype(int)
    team_summary["win_pct"] = np.where(team_summary["matches_played"] > 0, (team_summary["wins"] / team_summary["matches_played"] * 100).round(2), 0.0)
    team_summary = team_summary.sort_values("wins", ascending=False)

    toss = pd.DataFrame()
    if {"toss_winner", "winner"}.issubset(matches.columns):
        toss = (
            matches.assign(toss_match_win=matches["toss_winner"] == matches["winner"])
            .groupby("toss_winner")["toss_match_win"]
            .agg(["count", "sum"])
            .reset_index()
            .rename(columns={"toss_winner": "team", "count": "tosses", "sum": "matches_won_after_toss"})
        )
        toss["toss_win_pct"] = np.where(toss["tosses"] > 0, (toss["matches_won_after_toss"] / toss["tosses"] * 100).round(2), 0.0)

    bat_chase = pd.DataFrame()
    if {"win_by_runs", "win_by_wickets", "winner"}.issubset(matches.columns):
        bat_first_wins = matches.loc[matches["win_by_runs"] > 0, "winner"].value_counts().rename_axis("team").reset_index(name="batting_first_wins")
        chase_wins = matches.loc[matches["win_by_wickets"] > 0, "winner"].value_counts().rename_axis("team").reset_index(name="chasing_wins")
        bat_chase = matches_played.merge(bat_first_wins, on="team", how="left").merge(chase_wins, on="team", how="left").fillna(0)
        bat_chase[["batting_first_wins", "chasing_wins"]] = bat_chase[["batting_first_wins", "chasing_wins"]].astype(int)
    elif {"result", "winner"}.issubset(matches.columns):
        bat_first_wins = matches.loc[matches["result"].astype(str).str.lower() == "runs", "winner"].value_counts().rename_axis("team").reset_index(name="batting_first_wins")
        chase_wins = matches.loc[matches["result"].astype(str).str.lower() == "wickets", "winner"].value_counts().rename_axis("team").reset_index(name="chasing_wins")
        bat_chase = matches_played.merge(bat_first_wins, on="team", how="left").merge(chase_wins, on="team", how="left").fillna(0)
        bat_chase[["batting_first_wins", "chasing_wins"]] = bat_chase[["batting_first_wins", "chasing_wins"]].astype(int)

    return {"wins": team_summary, "win_pct": team_summary, "toss": toss, "bat_chase": bat_chase}

def render_player_metrics(deliveries: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    if deliveries.empty:
        return {"runs": pd.DataFrame(), "wickets": pd.DataFrame(), "strike": pd.DataFrame(), "economy": pd.DataFrame()}

    batsman_col = _first_existing_column(deliveries, ["batsman", "striker", "batter"])
    bowler_col = _first_existing_column(deliveries, ["bowler"])
    dismissal_col = _first_existing_column(deliveries, ["dismissal_kind"])
    dismissed_player_col = _first_existing_column(deliveries, ["player_dismissed"])

    runs = pd.DataFrame()
    strike = pd.DataFrame()
    wickets = pd.DataFrame()
    economy = pd.DataFrame()

    if batsman_col and "batsman_runs" in deliveries.columns:
        runs = deliveries.groupby(batsman_col)["batsman_runs"].sum().sort_values(ascending=False).reset_index().rename(columns={batsman_col: "player", "batsman_runs": "runs"})
        legal_balls = _numeric_or_zero_series(deliveries, "wide_runs") == 0
        balls_faced = deliveries.loc[legal_balls].groupby(batsman_col).size().rename("balls_faced").reset_index().rename(columns={batsman_col: "player"})
        strike = runs.merge(balls_faced, on="player", how="left").fillna(0)
        strike["strike_rate"] = np.where(strike["balls_faced"] > 0, (strike["runs"] / strike["balls_faced"] * 100).round(2), 0.0)

    if bowler_col and dismissed_player_col and dismissal_col:
        wicket_mask = deliveries[dismissal_col].str.lower().isin(VALID_WICKET_KINDS)
        wickets = (
            deliveries.loc[wicket_mask & deliveries[dismissed_player_col].notna() & (deliveries[dismissed_player_col] != "Unknown")]
            .groupby(bowler_col)[dismissed_player_col]
            .count()
            .sort_values(ascending=False)
            .reset_index()
            .rename(columns={bowler_col: "player", dismissed_player_col: "wickets"})
        )

    if bowler_col and "total_runs" in deliveries.columns:
        legal_balls = deliveries.loc[(_numeric_or_zero_series(deliveries, "wide_runs") == 0) & (_numeric_or_zero_series(deliveries, "noball_runs") == 0)]
        economy = legal_balls.groupby(bowler_col)["total_runs"].agg(["sum", "count"]).reset_index().rename(columns={bowler_col: "player", "sum": "runs_conceded", "count": "balls_bowled"})
        economy["overs_bowled"] = economy["balls_bowled"] / 6
        economy["economy_rate"] = np.where(economy["overs_bowled"] > 0, (economy["runs_conceded"] / economy["overs_bowled"]).round(2), 0.0)
        economy = economy.sort_values("economy_rate")

    return {"runs": runs, "wickets": wickets, "strike": strike, "economy": economy}

def render_venue_metrics(matches: pd.DataFrame, deliveries: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    if matches.empty or deliveries.empty:
        return {"venues": pd.DataFrame(), "wins": pd.DataFrame()}

    venue_col = _first_existing_column(matches, ["venue", "stadium"])
    match_id_col = _first_existing_column(matches, ["id", "match_id"])
    delivery_match_col = _first_existing_column(deliveries, ["match_id", "id"])

    venue_scores = pd.DataFrame()
    if venue_col and match_id_col and delivery_match_col:
        match_runs = deliveries.groupby(delivery_match_col)["total_runs"].sum().reset_index().rename(columns={delivery_match_col: match_id_col, "total_runs": "match_runs"})
        venue_scores = matches[[match_id_col, venue_col]].merge(match_runs, on=match_id_col, how="left")
        venue_scores = venue_scores.groupby(venue_col)["match_runs"].agg(["mean", "sum", "count"]).reset_index().rename(columns={venue_col: "venue", "mean": "avg_runs", "sum": "total_runs", "count": "matches"})
        venue_scores = venue_scores.sort_values("avg_runs", ascending=False)

    venue_wins = pd.DataFrame()
    if venue_col:
        if {"win_by_runs", "win_by_wickets", "winner"}.issubset(matches.columns):
            batting_first = matches.loc[matches["win_by_runs"] > 0].groupby(venue_col)["winner"].count().reset_index().rename(columns={venue_col: "venue", "winner": "batting_first_wins"})
            chasing = matches.loc[matches["win_by_wickets"] > 0].groupby(venue_col)["winner"].count().reset_index().rename(columns={venue_col: "venue", "winner": "chasing_wins"})
            venue_wins = batting_first.merge(chasing, on="venue", how="outer").fillna(0)
            venue_wins[["batting_first_wins", "chasing_wins"]] = venue_wins[["batting_first_wins", "chasing_wins"]].astype(int)
        elif {"result", "winner"}.issubset(matches.columns):
            batting_first = matches.loc[matches["result"].astype(str).str.lower() == "runs"].groupby(venue_col)["winner"].count().reset_index().rename(columns={venue_col: "venue", "winner": "batting_first_wins"})
            chasing = matches.loc[matches["result"].astype(str).str.lower() == "wickets"].groupby(venue_col)["winner"].count().reset_index().rename(columns={venue_col: "venue", "winner": "chasing_wins"})
            venue_wins = batting_first.merge(chasing, on="venue", how="outer").fillna(0)
            venue_wins[["batting_first_wins", "chasing_wins"]] = venue_wins[["batting_first_wins", "chasing_wins"]].astype(int)

    return {"venues": venue_scores, "wins": venue_wins}

def render_match_insights(matches: pd.DataFrame, deliveries: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    super_over = pd.DataFrame()
    if "is_super_over" in deliveries.columns:
        delivery_match_col = _first_existing_column(deliveries, ["match_id", "id"])
        if delivery_match_col:
            super_over = deliveries.groupby(delivery_match_col)["is_super_over"].sum().reset_index()
            super_over = super_over[super_over["is_super_over"] > 0]

    season_trend = pd.DataFrame()
    if {"season", "winner"}.issubset(matches.columns):
        season_trend = matches.groupby("season").agg(matches_played=("winner", "size"), unique_winners=("winner", "nunique")).reset_index()

    captain_col = _first_existing_column(matches, ["captain", "team_captain", "winner_captain"])
    captains = pd.DataFrame()
    if captain_col and "winner" in matches.columns:
        captains = matches.loc[matches[captain_col].notna() & (matches[captain_col] != "Unknown")].groupby(captain_col)["winner"].count().reset_index().rename(columns={captain_col: "captain", "winner": "wins"}).sort_values("wins", ascending=False)

    return {"super_over": super_over, "season_trend": season_trend, "captains": captains}



def screen_player_analysis(deliveries: pd.DataFrame, player_metrics: Dict, matches: pd.DataFrame) -> None:
    st.markdown('<div class="dashboard-header">PLAYER PERFORMANCE CONSOLE</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Explore leaderboards, run direct batter/bowler matchups, or compare statistics.</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🏆 Player Leaderboards", "⚔️ Head-to-Head Player Comparison", "🥊 Direct Batter vs. Bowler Duel"])

    with tab1:
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                runs = player_metrics["runs"].head(10)
                if not runs.empty:
                    fig = px.bar(runs, x="runs", y="player", orientation='h', title="Top Run Scorers", 
                                 color="runs", color_continuous_scale="Reds")
                    fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=360)
                    st.plotly_chart(update_plotly_layout(fig), use_container_width=True)
            with col2:
                wickets = player_metrics["wickets"].head(10)
                if not wickets.empty:
                    fig = px.bar(wickets, x="wickets", y="player", orientation='h', title="Top Wicket Takers", 
                                 color="wickets", color_continuous_scale="Tealgrn")
                    fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=360)
                    st.plotly_chart(update_plotly_layout(fig), use_container_width=True)

        with st.container(border=True):
            col3, col4 = st.columns(2)
            with col3:
                strike = player_metrics["strike"].loc[player_metrics["strike"]["runs"] > 150].sort_values("strike_rate", ascending=False).head(10)
                if not strike.empty:
                    fig = px.bar(strike, x="strike_rate", y="player", orientation='h', title="Highest Batting Strike Rates (Min 150 Runs)", 
                                 color="strike_rate", color_continuous_scale="Sunset")
                    fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=360)
                    st.plotly_chart(update_plotly_layout(fig), use_container_width=True)
            with col4:
                economy = player_metrics["economy"].loc[player_metrics["economy"]["balls_bowled"] > 120].sort_values("economy_rate", ascending=True).head(10)
                if not economy.empty:
                    fig = px.bar(economy, x="economy_rate", y="player", orientation='h', title="Most Economical Bowlers (Min 20 Overs)", 
                                 color="economy_rate", color_continuous_scale="Mako_r")
                    fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=360)
                    st.plotly_chart(update_plotly_layout(fig), use_container_width=True)

    with tab2:
        col_c1, col_c2, col_c3 = st.columns((2, 2, 1))
        
        batsmen_list = sorted(player_metrics["runs"]["player"].unique().tolist())
        bowlers_list = sorted(player_metrics["wickets"]["player"].unique().tolist())
        
        with col_c3:
            comp_role = st.radio("Select Role", ["Batsman", "Bowler"])
            
        with col_c1:
            p1_pool = batsmen_list if comp_role == "Batsman" else bowlers_list
            player_1 = st.selectbox("Select Player 1", p1_pool, index=0, key="comp_p1")
        with col_c2:
            p2_pool = [p for p in p1_pool if p != player_1]
            player_2 = st.selectbox("Select Player 2", p2_pool, index=0, key="comp_p2")

        with st.container(border=True):
            st.markdown(f"#### Career Statistical Comparison: {player_1} vs. {player_2}")
            
            if comp_role == "Batsman":
                p1_df = deliveries[deliveries['batter'] == player_1]
                p2_df = deliveries[deliveries['batter'] == player_2]
                
                p1_runs = p1_df['batsman_runs'].sum()
                p2_runs = p2_df['batsman_runs'].sum()
                
                p1_balls = len(p1_df[p1_df['extras_type'] != 'wides'])
                p2_balls = len(p2_df[p2_df['extras_type'] != 'wides'])
                
                p1_sr = (p1_runs / p1_balls * 100) if p1_balls > 0 else 0.0
                p2_sr = (p2_runs / p2_balls * 100) if p2_balls > 0 else 0.0
                
                p1_matches = p1_df['match_id'].nunique()
                p2_matches = p2_df['match_id'].nunique()
                
                p1_dismissals = len(p1_df[(p1_df['player_dismissed'] == player_1) & (p1_df['dismissal_kind'].str.lower().isin(VALID_WICKET_KINDS))])
                p2_dismissals = len(p2_df[(p2_df['player_dismissed'] == player_2) & (p2_df['dismissal_kind'].str.lower().isin(VALID_WICKET_KINDS))])
                
                p1_avg = (p1_runs / p1_dismissals) if p1_dismissals > 0 else p1_runs
                p2_avg = (p2_runs / p2_dismissals) if p2_dismissals > 0 else p2_runs
                
                p1_4s = len(p1_df[p1_df['batsman_runs'] == 4])
                p2_4s = len(p2_df[p2_df['batsman_runs'] == 4])
                
                p1_6s = len(p1_df[p1_df['batsman_runs'] == 6])
                p2_6s = len(p2_df[p2_df['batsman_runs'] == 6])
                
                metric_df = pd.DataFrame({
                    "Stat Metric": ["Matches Played", "Total Runs Scored", "Balls Faced", "Strike Rate", "Average", "Fours (4s)", "Sixes (6s)"],
                    player_1: [p1_matches, p1_runs, p1_balls, f"{p1_sr:.2f}", f"{p1_avg:.2f}", p1_4s, p1_6s],
                    player_2: [p2_matches, p2_runs, p2_balls, f"{p2_sr:.2f}", f"{p2_avg:.2f}", p2_4s, p2_6s]
                })
                st.dataframe(metric_df, use_container_width=True, hide_index=True)
                
                st.markdown("##### Seasonal Performance Progress")
                merged_p1 = deliveries[deliveries['batter'] == player_1]
                merged_p2 = deliveries[deliveries['batter'] == player_2]
                
                if 'season' in deliveries.columns:
                    p1_season = merged_p1.groupby('season')['batsman_runs'].sum().reset_index()
                    p2_season = merged_p2.groupby('season')['batsman_runs'].sum().reset_index()
                else:
                    merged_matches = matches[['id', 'season']].rename(columns={'id': 'match_id'})
                    merged_p1 = merged_p1.merge(merged_matches, on='match_id', how='left')
                    merged_p2 = merged_p2.merge(merged_matches, on='match_id', how='left')
                    p1_season = merged_p1.groupby('season')['batsman_runs'].sum().reset_index()
                    p2_season = merged_p2.groupby('season')['batsman_runs'].sum().reset_index()
                    
                p1_season['player'] = player_1
                p2_season['player'] = player_2
                combined_seasons = pd.concat([p1_season, p2_season])
                
                if not combined_seasons.empty:
                    fig = px.line(combined_seasons, x="season", y="batsman_runs", color="player", markers=True,
                                  title="Runs Scored Season-on-Season Comparison", labels={"season": "Season", "batsman_runs": "Runs"})
                    st.plotly_chart(update_plotly_layout(fig), use_container_width=True)
                    
            else: # Bowlers
                p1_df = deliveries[deliveries['bowler'] == player_1]
                p2_df = deliveries[deliveries['bowler'] == player_2]
                
                wicket_mask_p1 = p1_df['dismissal_kind'].str.lower().isin(VALID_WICKET_KINDS)
                wicket_mask_p2 = p2_df['dismissal_kind'].str.lower().isin(VALID_WICKET_KINDS)
                
                p1_w = len(p1_df[wicket_mask_p1 & p1_df['player_dismissed'].notna() & (p1_df['player_dismissed'] != 'Unknown')])
                p2_w = len(p2_df[wicket_mask_p2 & p2_df['player_dismissed'].notna() & (p2_df['player_dismissed'] != 'Unknown')])
                
                p1_balls = len(p1_df[(p1_df['extras_type'] != 'wides') & (p1_df['extras_type'] != 'noballs')])
                p2_balls = len(p2_df[(p2_df['extras_type'] != 'wides') & (p2_df['extras_type'] != 'noballs')])
                
                p1_overs = p1_balls / 6
                p2_overs = p2_balls / 6
                
                p1_runs = p1_df[~p1_df['extras_type'].isin(['byes', 'legbyes'])]['total_runs'].sum()
                p2_runs = p2_df[~p2_df['extras_type'].isin(['byes', 'legbyes'])]['total_runs'].sum()
                
                p1_econ = (p1_runs / p1_overs) if p1_overs > 0 else 0.0
                p2_econ = (p2_runs / p2_overs) if p2_overs > 0 else 0.0
                
                p1_matches = p1_df['match_id'].nunique()
                p2_matches = p2_df['match_id'].nunique()
                
                p1_sr = (p1_balls / p1_w) if p1_w > 0 else 0.0
                p2_sr = (p2_balls / p2_w) if p2_w > 0 else 0.0
                
                p1_avg = (p1_runs / p1_w) if p1_w > 0 else p1_runs
                p2_avg = (p2_runs / p2_w) if p2_w > 0 else 0.0
                
                metric_df = pd.DataFrame({
                    "Stat Metric": ["Matches Played", "Overs Bowled", "Wickets Taken", "Economy Rate", "Strike Rate", "Average Runs Conceded/Wicket"],
                    player_1: [p1_matches, f"{p1_overs:.1f}", p1_w, f"{p1_econ:.2f}", f"{p1_sr:.2f}", f"{p1_avg:.2f}"],
                    player_2: [p2_matches, f"{p2_overs:.1f}", p2_w, f"{p2_econ:.2f}", f"{p2_sr:.2f}", f"{p2_avg:.2f}"]
                })
                st.dataframe(metric_df, use_container_width=True, hide_index=True)
                
                st.markdown("##### Seasonal Performance Progress")
                if 'season' in deliveries.columns:
                    p1_w_mask = wicket_mask_p1 & p1_df['player_dismissed'].notna() & (p1_df['player_dismissed'] != 'Unknown')
                    p2_w_mask = wicket_mask_p2 & p2_df['player_dismissed'].notna() & (p2_df['player_dismissed'] != 'Unknown')
                    
                    p1_season = p1_df[p1_w_mask].groupby('season').size().reset_index(name='wickets')
                    p2_season = p2_df[p2_w_mask].groupby('season').size().reset_index(name='wickets')
                else:
                    merged_matches = matches[['id', 'season']].rename(columns={'id': 'match_id'})
                    p1_df = p1_df.merge(merged_matches, on='match_id', how='left')
                    p2_df = p2_df.merge(merged_matches, on='match_id', how='left')
                    p1_w_mask = p1_df['dismissal_kind'].str.lower().isin(VALID_WICKET_KINDS) & p1_df['player_dismissed'].notna() & (p1_df['player_dismissed'] != 'Unknown')
                    p2_w_mask = p2_df['dismissal_kind'].str.lower().isin(VALID_WICKET_KINDS) & p2_df['player_dismissed'].notna() & (p2_df['player_dismissed'] != 'Unknown')
                    
                    p1_season = p1_df[p1_w_mask].groupby('season').size().reset_index(name='wickets')
                    p2_season = p2_df[p2_w_mask].groupby('season').size().reset_index(name='wickets')
                    
                p1_season['player'] = player_1
                p2_season['player'] = player_2
                combined_seasons = pd.concat([p1_season, p2_season])
                
                if not combined_seasons.empty:
                    fig = px.line(combined_seasons, x="season", y="wickets", color="player", markers=True,
                                  title="Wickets Taken Season-on-Season Comparison", labels={"season": "Season", "wickets": "Wickets"})
                    st.plotly_chart(update_plotly_layout(fig), use_container_width=True)

    with tab3:
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            selected_batsman = st.selectbox("Select Batter", batsmen_list, index=0, key="duel_bat")
        with col_d2:
            selected_bowler = st.selectbox("Select Bowler", bowlers_list, index=0, key="duel_bowl")
            
        result = compute_player_matchup(deliveries, selected_batsman, selected_bowler)
        
        with st.container(border=True):
            st.markdown(f"#### Head-to-Head Duel: {selected_batsman} vs. {selected_bowler}")
            
            if not result:
                st.info(f"No direct ball-by-ball clashes recorded between {selected_batsman} and {selected_bowler} in the current dataset.")
            else:
                dc1, dc2, dc3, dc4 = st.columns(4)
                with dc1:
                    st.metric("Runs Scored", f"{result['runs']}")
                with dc2:
                    st.metric("Balls Faced", f"{result['balls']}")
                with dc3:
                    st.metric("Dismissals", f"{result['dismissals']}")
                with dc4:
                    st.metric("Strike Rate", f"{result['strike_rate']}")
                    
                st.markdown("---")
                dc5, dc6, dc7 = st.columns(3)
                with dc5:
                    st.metric("Fours (4s)", f"{result['fours']}")
                with dc6:
                    st.metric("Sixes (6s)", f"{result['sixes']}")
                with dc7:
                    st.metric("Dot Balls", f"{result['dots']}")

def screen_venue_analysis(venue_metrics: Dict) -> None:
    st.markdown('<div class="dashboard-header">VENUE INTELLIGENCE</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Identify high-scoring stadiums and analyze batting patterns by ground.</div>', unsafe_allow_html=True)

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            venues = venue_metrics["venues"].head(10)
            if not venues.empty:
                fig = px.bar(venues, x="avg_runs", y="venue", orientation='h', title="Highest Average Runs by Ground", 
                             color="avg_runs", color_continuous_scale="Oranges")
                fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=360)
                st.plotly_chart(update_plotly_layout(fig), use_container_width=True)
                
        with col2:
            if not venues.empty:
                fig = px.scatter(venues, x="matches", y="avg_runs", size="total_runs", hover_name="venue", 
                                 title="Venue Density (Matches Played vs. Avg Runs)")
                fig.update_layout(height=360)
                st.plotly_chart(update_plotly_layout(fig), use_container_width=True)

    with st.container(border=True):
        venue_wins = venue_metrics["wins"].head(10)
        if not venue_wins.empty:
            plot_df = venue_wins.melt(id_vars="venue", value_vars=["batting_first_wins", "chasing_wins"], 
                                     var_name="Win Condition", value_name="Wins")
            plot_df["Win Condition"] = plot_df["Win Condition"].map({"batting_first_wins": "Batting First Wins", "chasing_wins": "Chasing Wins"})
            fig = px.bar(plot_df, x="venue", y="Wins", color="Win Condition", barmode="group", title="Ground Success Matrix (Batting vs. Chasing Wins)")
            fig.update_layout(height=360)
            st.plotly_chart(update_plotly_layout(fig), use_container_width=True)

def screen_predict_winner(matches: pd.DataFrame) -> None:
    st.markdown('<div class="dashboard-header">IPL MATCH PREDICTOR ENGINE</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Machine-assisted win probability calculations using historical matrices.</div>', unsafe_allow_html=True)

    teams = get_team_pool(matches)
    
    col1, col2 = st.columns(2)
    with col1:
        team_a = st.selectbox("Select Team A", teams, index=0, key="pred_ta")
    with col2:
        team_b = st.selectbox("Select Team B", [t for t in teams if t != team_a], index=0, key="pred_tb")
        
    venues = sorted(matches["venue"].dropna().unique().tolist())
    
    col3, col4, col5 = st.columns(3)
    with col3:
        venue = st.selectbox("Select Ground/Venue", venues, index=0)
    with col4:
        toss_winner = st.selectbox("Toss Winner Choice", [team_a, team_b], index=0)
    with col5:
        toss_decision = st.selectbox("Toss Decision", ["field", "bat"], index=0)
        
    if st.button("🔥 Run Prediction Analysis", use_container_width=True):
        result = compute_match_prediction(matches, team_a, team_b, venue, toss_winner, toss_decision)
        
        st.markdown(f"""
        <div class="predictor-container">
            <h3 style="text-align: center; color: white; margin-top:0;">Predictive Analysis Results</h3>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                <span style="font-weight: 800; color: #3b82f6; font-size: 1.25rem;">{team_a}</span>
                <span style="font-weight: 800; color: #f97316; font-size: 1.25rem;">{team_b}</span>
            </div>
            <div class="probability-bar-container">
                <div class="prob-team-a" style="width: {result['team_a_prob']}%">{result['team_a_prob']}%</div>
                <div class="prob-team-b" style="width: {result['team_b_prob']}%">{result['team_b_prob']}%</div>
            </div>
            <p style="text-align: center; font-size: 0.95rem; color: #94a3b8; margin-bottom:0;">
                Calculated using Head-to-Head strength, Venue records, Current season form, and Toss advantage.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container(border=True):
            st.subheader("Statistical Factor Breakdown")
            
            factors_df = pd.DataFrame({
                "Weighted Metric Factor": ["Head-to-Head win rate", "Venue success rate", "Recent team form", "Toss & decision effect"],
                f"{team_a} Weight Contribution": [result['h2h_factor'], result['venue_factor'], result['form_factor'], result['toss_factor']],
                f"{team_b} Weight Contribution": [100 - result['h2h_factor'], 100 - result['venue_factor'], 100 - result['form_factor'], 100 - result['toss_factor']]
            })
            
            col_f1, col_f2 = st.columns((3, 2))
            with col_f1:
                st.dataframe(factors_df, use_container_width=True, hide_index=True)
                
            with col_f2:
                plot_factors = pd.DataFrame({
                    "Factor": ["Head-to-Head", "Venue Success", "Recent Form", "Toss Influence"],
                    team_a: [result['h2h_factor'], result['venue_factor'], result['form_factor'], result['toss_factor']],
                    team_b: [100 - result['h2h_factor'], 100 - result['venue_factor'], 100 - result['form_factor'], 100 - result['toss_factor']]
                })
                melt_factors = plot_factors.melt(id_vars="Factor", var_name="Team", value_name="Success Weight")
                fig = px.bar(melt_factors, x="Factor", y="Success Weight", color="Team", barmode="group",
                             title="Probability Driver Comparison")
                st.plotly_chart(update_plotly_layout(fig), use_container_width=True)
                
            st.markdown("##### 📌 Strategic Context Breakdown")
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                st.markdown(f"""
                * **Head-to-Head Summary**: {team_a} and {team_b} have clashed **{result['total_h2h']}** times in the dataset. {team_a} won **{result['h2h_wins_a']}** matches, while {team_b} won **{result['h2h_wins_b']}** matches.
                * **Venue Adaptability**: {team_a} has played **{result['venue_matches_a']}** matches at this venue, and {team_b} has played **{result['venue_matches_b']}** matches here.
                """)
            with col_e2:
                st.markdown(f"""
                * **Recent Form Summary (Last 8 Matches)**: {team_a} was victorious in **{result['form_wins_a']}** games, and {team_b} emerged victorious in **{result['form_wins_b']}** games.
                * **Toss Advantage**: Teams batting first at this venue win approximately **{result['toss_factor']}%** of matches. Toss winner **{toss_winner}** has chosen to **{toss_decision}** first.
                """)

def screen_fantasy_builder(deliveries: pd.DataFrame, seasons: List[int]) -> None:
    st.markdown('<div class="dashboard-header">SMART FANTASY XI SELECTOR</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Algorithmic generation of optimal lineups based on player metrics and team strategies.</div>', unsafe_allow_html=True)

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        sel_season = st.selectbox("Select Season Pool", seasons, index=len(seasons)-1)
    with col_s2:
        strategy = st.selectbox("Select Team Strategy", ["Balanced XI", "Batting-Heavy XI", "Bowling-Heavy XI"])

    if 'season' in deliveries.columns:
        season_deliveries = deliveries[deliveries['season'] == sel_season]
    else:
        matches, _ = load_data()
        cleaned_m = clean_matches(matches)
        merged_del = filter_deliveries(deliveries, cleaned_m[cleaned_m['season'] == sel_season])
        season_deliveries = merged_del
        
    if season_deliveries.empty:
        st.info("No delivery logs available for the selected season. Try choosing another season.")
        return

    if st.button("🚀 Calculate Dream XI Lineup", use_container_width=True):
        with st.spinner("Processing player metrics..."):
            lineup = build_fantasy_xi(season_deliveries, strategy)
            
        if not lineup:
            st.warning("Insufficient player statistics found to construct a viable XI for this season.")
        else:
            with st.container(border=True):
                st.subheader(f"Optimal Fantasy Lineup - {strategy} ({sel_season})")
                
                cards_html = ""
                for player in lineup:
                    p_name = player['player']
                    role = player['role']
                    role_detail = player['role_detail']
                    score = player['fantasy_score']
                    
                    c_class = "role-bat"
                    t_class = "tag-bat"
                    if role == "Wicketkeeper":
                        c_class = "role-wk"
                        t_class = "tag-wk"
                    elif role == "All-Rounder":
                        c_class = "role-ar"
                        t_class = "tag-ar"
                    elif role == "Bowler":
                        c_class = "role-bowl"
                        t_class = "tag-bowl"
                        
                    role_badge_html = f'<div class="role-tag {t_class}">{role}</div>'
                    
                    detail_badge_html = ""
                    if role_detail != "Player":
                        detail_badge_html = f'<div style="font-weight:800; color:#ef4444; font-size:0.75rem; text-transform:uppercase; margin-top:2px;">{role_detail}</div>'
                        
                    stats_str = ""
                    if role in ["Batsman", "Wicketkeeper", "All-Rounder"]:
                        stats_str += f"<span style='font-size:0.8rem; color:#94a3b8;'>Runs: <b>{int(player['runs'])}</b> | SR: <b>{player['strike_rate']:.1f}</b></span>"
                    if role in ["Bowler", "All-Rounder"]:
                        if stats_str:
                            stats_str += "<br/>"
                        stats_str += f"<span style='font-size:0.8rem; color:#94a3b8;'>Wickets: <b>{int(player['wickets'])}</b> | Econ: <b>{player['economy']:.1f}</b></span>"
                        
                    cards_html += (
                        f'<div class="player-badge {c_class}">'
                        f'<h5 style="margin: 0 0 5px 0; color:white; font-size:1.05rem;">{p_name}</h5>'
                        f'{detail_badge_html}'
                        f'{role_badge_html}'
                        f'<div style="margin-top:10px;">{stats_str}</div>'
                        f'</div>'
                    )
                    
                st.markdown(f'<div class="lineup-grid">{cards_html}</div>', unsafe_allow_html=True)

# 14. Main Entry Point
def main() -> None:
    st.sidebar.markdown(
        """
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="color: #38bdf8; margin: 0; font-weight:800;">IPL CONSOLE</h2>
            <span style="color: #94a3b8; font-size: 0.8rem;">PRO ANALYTICS & PREDICTION</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if not os.path.exists(MATCHES_FILE) or not os.path.exists(DELIVERIES_FILE):
        st.title("IPL Data Analytics Dashboard")
        st.warning("Upload `matches.csv` and `deliveries.csv` into the dataset folder to launch the dashboard.")
        st.info(f"Expected paths:\n- {MATCHES_FILE}\n- {DELIVERIES_FILE}")
        return

    raw_matches, raw_deliveries = load_data()
    prepared = prepare_data(raw_matches, raw_deliveries)
    
    matches = prepared["matches"]
    deliveries = prepared["deliveries"]
    
    teams = get_team_pool(matches)
    seasons = get_season_pool(matches)
    
    with st.sidebar:
        navigation = st.radio(
            "Navigate Console",
            [
                "🏠 Dashboard Overview", 
                "📊 Team Performance & H2H", 
                "👤 Player Stats & Battle", 
                "🏟️ Venue Intelligence", 
                "🔮 Match Predictor Engine",
                "🏆 Smart Fantasy XI Builder"
            ]
        )
        st.markdown("---")
        
        with st.container(border=True):
            st.markdown("<div style='font-size: 0.95rem; font-weight: 700; color: #38bdf8; margin-bottom: 8px;'>🔧 Global Console Filters</div>", unsafe_allow_html=True)
            selected_team = st.selectbox("Franchise Filter", ["All Teams"] + teams)
            selected_seasons = st.multiselect(
                "Season Filter", 
                seasons, 
                default=seasons[-5:] if len(seasons) > 5 else seasons
            )
        
    filtered_matches = filter_matches(matches, selected_seasons, selected_team)
    if not filtered_matches.empty:
        filtered_deliveries = filter_deliveries(deliveries, filtered_matches)
    else:
        filtered_deliveries = pd.DataFrame()

    team_metrics = render_team_metrics(filtered_matches)
    player_metrics = render_player_metrics(filtered_deliveries)
    venue_metrics = render_venue_metrics(filtered_matches, filtered_deliveries)
    match_metrics = render_match_insights(filtered_matches, filtered_deliveries)

    # Import UI screens here to avoid circular imports at module load
    import ui.screens as ui_screens

    # Split the emoji from the navigation to route clean text
    nav_clean = navigation.split(" ", 1)[1] if " " in navigation else navigation

    if nav_clean == "Dashboard Overview":
        ui_screens.screen_overview(filtered_matches, filtered_deliveries, team_metrics, player_metrics, venue_metrics, match_metrics)
    elif nav_clean == "Team Performance & H2H":
        ui_screens.screen_team_analysis(filtered_matches, team_metrics)
    elif nav_clean == "Player Stats & Battle":
        ui_screens.screen_player_analysis(filtered_deliveries, player_metrics, filtered_matches)
    elif nav_clean == "Venue Intelligence":
        ui_screens.screen_venue_analysis(venue_metrics)
    elif nav_clean == "Match Predictor Engine":
        ui_screens.screen_predict_winner(matches)
    elif nav_clean == "Smart Fantasy XI Builder":
        ui_screens.screen_fantasy_builder(deliveries, seasons)

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "<span style='color: #475569; font-size: 0.75rem;'>IPL Console v2.0 • Pro Edition</span>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()