import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Dict, List

import app as _app
from app import (
    update_plotly_layout,
    get_team_pool,
    get_season_pool,
    filter_deliveries,
    build_fantasy_xi,
    compute_player_matchup,
    compute_match_prediction,
    load_data,
    clean_matches,
)
from ui import components as comp

# Note: this file contains UI renderers moved from the monolithic app.py

def render_header(title: str, subheader: str) -> None:
    st.markdown(
        f"""
        <div class="header-container">
            <h1 class="dashboard-header">{title}</h1>
            <p class="dashboard-subheader">{subheader}</p>
            <div class="header-accent-line"></div>
        </div>
        """,
        unsafe_allow_html=True
    )

def screen_overview(matches: pd.DataFrame, deliveries: pd.DataFrame, team_metrics: Dict, player_metrics: Dict, venue_metrics: Dict, match_metrics: Dict) -> None:
    render_header("IPL PRO ANALYTICS CONSOLE", "Premium cricket insights powered by dynamic dataset parsing and statistical engines.")
    # KPI card row (modern look)
    k1, k2, k3 = st.columns(3)
    total_matches = len(matches)
    total_teams = team_metrics['wins']['team'].nunique() if not team_metrics['wins'].empty else len(get_team_pool(matches))
    total_seasons = matches['season'].nunique() if 'season' in matches.columns else 0

    # Highest team/inning score (best attempt using deliveries)
    highest_score = None
    match_id_col = _app._first_existing_column(deliveries, ["match_id", "id"]) if isinstance(deliveries, pd.DataFrame) else None
    try:
        if match_id_col and 'inning' in deliveries.columns and 'total_runs' in deliveries.columns:
            inning_scores = deliveries.groupby([match_id_col, 'inning'])['total_runs'].sum()
            highest_score = int(inning_scores.max()) if not inning_scores.empty else None
    except Exception:
        highest_score = None

    # Top run scorer and wicket taker
    top_batsman = None
    top_wicket = None
    # Safely extract top player names from DataFrames without relying on positional keys
    if player_metrics.get('runs') is not None and not player_metrics['runs'].empty:
        runs_df = player_metrics['runs']
        if isinstance(runs_df, pd.DataFrame):
            # prefer a column named 'player' or fallback to first column
            if 'player' in runs_df.columns:
                top_batsman = runs_df.iloc[0]['player']
            else:
                top_batsman = runs_df.iloc[0, 0]
        else:
            top_batsman = str(runs_df.iloc[0])
    if player_metrics.get('wickets') is not None and not player_metrics['wickets'].empty:
        wk_df = player_metrics['wickets']
        if isinstance(wk_df, pd.DataFrame):
            if 'player' in wk_df.columns:
                top_wicket = wk_df.iloc[0]['player']
            else:
                top_wicket = wk_df.iloc[0, 0]
        else:
            top_wicket = str(wk_df.iloc[0])

    with k1:
        comp.kpi_card('Total Matches', f"{total_matches:,}", subtitle=f"Seasons: {total_seasons}", icon='📅')
    with k2:
        comp.kpi_card('Active Teams', f"{total_teams}", subtitle=f"Top: {top_batsman if top_batsman else '—'}", icon='👥')
    with k3:
        comp.kpi_card('Highest Inning Score', f"{highest_score if highest_score else '—'}", subtitle='Best single-innings team score', icon='💥')

    k4, k5, k6 = st.columns(3)
    with k4:
        comp.kpi_card('Seasons Tracked', f"{total_seasons}", icon='🏟️')
    with k5:
        comp.kpi_card('Top Run Scorer', f"{top_batsman if top_batsman else '—'}", icon='🥇')
    with k6:
        comp.kpi_card('Top Wicket Taker', f"{top_wicket if top_wicket else '—'}", icon='🎯')

    with st.container(border=True):
        st.subheader("Key Performance Overview")
        
        col1, col2 = st.columns(2)
        with col1:
            if not team_metrics["wins"].empty:
                top_teams = team_metrics["wins"].head(8)
                fig = px.bar(top_teams, x="wins", y="team", color="wins", orientation='h', 
                             title="Most Matches Won by Franchise", color_continuous_scale="Viridis")
                fig.update_layout(height=350, yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(update_plotly_layout(fig), use_container_width=True)
                
        with col2:
            if not player_metrics["runs"].empty:
                top_batsmen = player_metrics["runs"].head(8)
                fig = px.bar(top_batsmen, x="player", y="runs", color="runs", 
                             title="IPL All-Time Run Leaders", color_continuous_scale="Purples")
                fig.update_layout(height=350)
                st.plotly_chart(update_plotly_layout(fig), use_container_width=True)

    if not match_metrics["season_trend"].empty:
        with st.container(border=True):
            fig = px.area(match_metrics["season_trend"], x="season", y="matches_played", 
                          title="IPL Matches Distribution by Season", line_shape="spline", markers=True)
            fig.update_layout(height=320)
            st.plotly_chart(update_plotly_layout(fig), use_container_width=True)

    # Key Insights section
    insights = comp.compute_insights(matches, deliveries)
    if insights:
        with st.container(border=True):
            st.subheader('Key Insights')
            col_i1, col_i2, col_i3 = st.columns(3)
            with col_i1:
                st.markdown(f"**Best Team:** {insights.get('best_team','—')} ({insights.get('best_team_wins',0)} wins)")
            with col_i2:
                st.markdown(f"**Toss Influence:** {insights.get('toss_win_pct','—')}% matches won by toss winner")
            with col_i3:
                top_cons = insights.get('top_consistent_batters', [])
                st.markdown(f"**Consistent Players:** {', '.join(top_cons) if top_cons else '—'}")

def screen_team_analysis(matches: pd.DataFrame, team_metrics: Dict) -> None:
    render_header("TEAM PERFORMANCE & H2H", "Compare franchise strength and analyze direct matchups.")

    tab1, tab2 = st.tabs(["📊 Franchise Standings", "⚔️ Head-to-Head Arena"])
    
    with tab1:
        with st.container(border=True):
            col1, col2 = st.columns((2, 3))
            
            with col1:
                st.markdown("<div style='font-size: 1.15rem; font-weight: 700; color: #38bdf8; margin-bottom: 12px;'>📊 Overall Standings Matrix</div>", unsafe_allow_html=True)
                win_pct = team_metrics["win_pct"].sort_values("win_pct", ascending=False)
                st.dataframe(
                    win_pct[["team", "matches_played", "wins", "win_pct"]].rename(
                        columns={
                            "team": "Franchise", "matches_played": "Played", 
                            "wins": "Wins", "win_pct": "Win %"
                        }
                    ),
                    use_container_width=True, hide_index=True
                )
                
            with col2:
                bat_chase = team_metrics["bat_chase"].copy()
                if not bat_chase.empty:
                    bat_chase["total_wins"] = bat_chase["batting_first_wins"] + bat_chase["chasing_wins"]
                    bat_chase = bat_chase.sort_values("total_wins", ascending=False).head(8)
                    plot_df = bat_chase.melt(id_vars="team", value_vars=["batting_first_wins", "chasing_wins"], 
                                             var_name="Win Mode", value_name="Wins")
                    plot_df["Win Mode"] = plot_df["Win Mode"].map({"batting_first_wins": "Defending Target", "chasing_wins": "Chasing Target"})
                    fig = px.bar(plot_df, x="team", y="Wins", color="Win Mode", barmode="group",
                                 title="Defending vs. Chasing Wins Analysis")
                    fig.update_layout(height=380, xaxis_title="Team", yaxis_title="Matches Won")
                    st.plotly_chart(update_plotly_layout(fig), use_container_width=True)
        
        with st.container(border=True):
            toss = team_metrics["toss"].sort_values("toss_win_pct", ascending=False).head(10)
            if not toss.empty:
                fig = px.scatter(toss, x="tosses", y="toss_win_pct", size="matches_won_after_toss", color="team", 
                                 title="Toss Winning Impact and Correlation", hover_data=["matches_won_after_toss"])
                fig.update_layout(height=380, xaxis_title="Total Tosses Won", yaxis_title="Win % After Winning Toss")
                st.plotly_chart(update_plotly_layout(fig), use_container_width=True)

    with tab2:
        teams = get_team_pool(matches)
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            team_a = st.selectbox("Select Team 1", teams, index=0, key="h2h_t1")
        with col_s2:
            team_b = st.selectbox("Select Team 2", [t for t in teams if t != team_a], index=0, key="h2h_t2")
            
        h2h_matches = matches[((matches['team1'] == team_a) & (matches['team2'] == team_b)) | 
                              ((matches['team1'] == team_b) & (matches['team2'] == team_a))]
        
        if h2h_matches.empty:
            st.info("No historical matches found between these two teams in the current filtered dataset.")
        else:
            total_matches = len(h2h_matches)
            wins_a = len(h2h_matches[h2h_matches['winner'] == team_a])
            wins_b = len(h2h_matches[h2h_matches['winner'] == team_b])
            others = total_matches - (wins_a + wins_b)
            
            with st.container(border=True):
                st.markdown(f"<div style='font-size: 1.25rem; font-weight: 800; color: #38bdf8; margin-bottom: 12px;'>⚔️ {team_a} vs. {team_b} Head-to-Head Stats</div>", unsafe_allow_html=True)
                
                mc1, mc2, mc3 = st.columns(3)
                with mc1:
                    st.metric(f"Total Encounters", f"{total_matches}")
                with mc2:
                    st.metric(f"{team_a} Wins", f"{wins_a}", delta=f"{(wins_a/total_matches*100):.1f}% of total" if total_matches>0 else None)
                with mc3:
                    st.metric(f"{team_b} Wins", f"{wins_b}", delta=f"{(wins_b/total_matches*100):.1f}% of total" if total_matches>0 else None)
            
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                with st.container(border=True):
                    pie_df = pd.DataFrame({
                        "Outcome": [team_a, team_b] + (["No Result/Tie"] if others > 0 else []),
                        "Wins": [wins_a, wins_b] + ([others] if others > 0 else [])
                    })
                    fig = px.pie(pie_df, values="Wins", names="Outcome", title="Match Win Distribution")
                    st.plotly_chart(update_plotly_layout(fig), use_container_width=True)
                
            with col_g2:
                with st.container(border=True):
                    st.markdown("<div style='font-size: 1.1rem; font-weight: 700; color: #38bdf8; margin-bottom: 8px;'>🪙 Toss Winning Patterns</div>", unsafe_allow_html=True)
                    toss_wins_a = len(h2h_matches[h2h_matches['toss_winner'] == team_a])
                    toss_wins_b = len(h2h_matches[h2h_matches['toss_winner'] == team_b])
                    
                    toss_pie = pd.DataFrame({
                        "Toss Winner": [team_a, team_b],
                        "Tosses Won": [toss_wins_a, toss_wins_b]
                    })
                    fig = px.pie(toss_pie, values="Tosses Won", names="Toss Winner", title="Toss Wins Distribution")
                    st.plotly_chart(update_plotly_layout(fig), use_container_width=True)
                
            with st.container(border=True):
                st.markdown("<div style='font-size: 1.1rem; font-weight: 700; color: #38bdf8; margin-bottom: 12px;'>📋 Last 5 Match Encounters History</div>", unsafe_allow_html=True)
                recent_encounters = h2h_matches.sort_values("date", ascending=False).head(5)
                st.dataframe(
                    recent_encounters[["date", "venue", "toss_winner", "toss_decision", "winner", "result_margin", "result"]].rename(
                        columns={
                            "date": "Date", "venue": "Venue", "toss_winner": "Toss Winner", 
                            "toss_decision": "Toss Choice", "winner": "Winner", 
                            "result_margin": "Margin", "result": "Won By"
                        }
                    ),
                    use_container_width=True, hide_index=True
                )

def screen_player_analysis(deliveries: pd.DataFrame, player_metrics: Dict, matches: pd.DataFrame) -> None:
    render_header("PLAYER PERFORMANCE CONSOLE", "Explore leaderboards, run direct batter/bowler matchups, or compare statistics.")

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
            st.markdown(f"<div style='font-size: 1.2rem; font-weight: 800; color: #38bdf8; margin-bottom: 12px;'>⚔️ Career Statistical Comparison: {player_1} vs. {player_2}</div>", unsafe_allow_html=True)
            
            # Detect actual column names used in deliveries
            batter_col = _app._first_existing_column(deliveries, ['batsman', 'striker', 'batter'])
            bowler_col = _app._first_existing_column(deliveries, ['bowler'])
            dismissal_col = _app._first_existing_column(deliveries, ['dismissal_kind'])
            dismissed_player_col = _app._first_existing_column(deliveries, ['player_dismissed', 'player_out'])
            match_id_col = _app._first_existing_column(deliveries, ['match_id', 'id'])

            if comp_role == "Batsman":
                if batter_col:
                    p1_df = deliveries[deliveries[batter_col] == player_1]
                    p2_df = deliveries[deliveries[batter_col] == player_2]
                else:
                    p1_df = pd.DataFrame()
                    p2_df = pd.DataFrame()
                
                p1_runs = p1_df['batsman_runs'].sum()
                p2_runs = p2_df['batsman_runs'].sum()
                
                p1_balls = len(p1_df[p1_df['extras_type'] != 'wides'])
                p2_balls = len(p2_df[p2_df['extras_type'] != 'wides'])
                
                p1_sr = (p1_runs / p1_balls * 100) if p1_balls > 0 else 0.0
                p2_sr = (p2_runs / p2_balls * 100) if p2_balls > 0 else 0.0
                
                p1_matches = p1_df[match_id_col].nunique() if (match_id_col and match_id_col in p1_df.columns) else p1_df.shape[0]
                p2_matches = p2_df[match_id_col].nunique() if (match_id_col and match_id_col in p2_df.columns) else p2_df.shape[0]
                
                if dismissed_player_col and dismissal_col:
                    p1_dismissals = len(p1_df[(p1_df[dismissed_player_col] == player_1) & (p1_df[dismissal_col].str.lower().isin(_app.VALID_WICKET_KINDS))])
                    p2_dismissals = len(p2_df[(p2_df[dismissed_player_col] == player_2) & (p2_df[dismissal_col].str.lower().isin(_app.VALID_WICKET_KINDS))])
                else:
                    p1_dismissals = 0
                    p2_dismissals = 0
                
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
                
                st.markdown("<div style='font-size: 1.1rem; font-weight: 700; color: #38bdf8; margin-bottom: 12px; margin-top: 15px;'>📈 Seasonal Run Accumulation</div>", unsafe_allow_html=True)
                merged_p1 = deliveries[deliveries[batter_col] == player_1] if batter_col else pd.DataFrame()
                merged_p2 = deliveries[deliveries[batter_col] == player_2] if batter_col else pd.DataFrame()
                
                if 'season' in deliveries.columns:
                    p1_season = merged_p1.groupby('season')['batsman_runs'].sum().reset_index() if not merged_p1.empty else pd.DataFrame()
                    p2_season = merged_p2.groupby('season')['batsman_runs'].sum().reset_index() if not merged_p2.empty else pd.DataFrame()
                else:
                    merged_matches = _app.load_data()[0][['id', 'season']].rename(columns={'id': 'match_id'})
                    key = match_id_col or 'match_id'
                    if key in merged_p1.columns:
                        merged_p1 = merged_p1.merge(merged_matches, left_on=key, right_on='match_id', how='left')
                    if key in merged_p2.columns:
                        merged_p2 = merged_p2.merge(merged_matches, left_on=key, right_on='match_id', how='left')
                    p1_season = merged_p1.groupby('season')['batsman_runs'].sum().reset_index()
                    p2_season = merged_p2.groupby('season')['batsman_runs'].sum().reset_index()
                    
                if not p1_season.empty:
                    p1_season['player'] = player_1
                if not p2_season.empty:
                    p2_season['player'] = player_2
                combined_seasons = pd.concat([p1_season, p2_season])
                
                if not combined_seasons.empty:
                    fig = px.line(combined_seasons, x="season", y="batsman_runs", color="player", markers=True,
                                  title="Runs Scored Season-on-Season Comparison", labels={"season": "Season", "batsman_runs": "Runs"})
                    st.plotly_chart(update_plotly_layout(fig), use_container_width=True)
                    
            else: # Bowlers
                if bowler_col:
                    p1_df = deliveries[deliveries[bowler_col] == player_1]
                    p2_df = deliveries[deliveries[bowler_col] == player_2]
                else:
                    p1_df = pd.DataFrame()
                    p2_df = pd.DataFrame()

                if dismissal_col and dismissal_col in p1_df.columns:
                    wicket_mask_p1 = p1_df[dismissal_col].str.lower().isin(_app.VALID_WICKET_KINDS)
                else:
                    wicket_mask_p1 = pd.Series(False, index=p1_df.index)
                if dismissal_col and dismissal_col in p2_df.columns:
                    wicket_mask_p2 = p2_df[dismissal_col].str.lower().isin(_app.VALID_WICKET_KINDS)
                else:
                    wicket_mask_p2 = pd.Series(False, index=p2_df.index)

                if dismissed_player_col and dismissed_player_col in p1_df.columns:
                    p1_w = len(p1_df[wicket_mask_p1 & p1_df[dismissed_player_col].notna() & (p1_df[dismissed_player_col] != 'Unknown')])
                else:
                    p1_w = 0
                if dismissed_player_col and dismissed_player_col in p2_df.columns:
                    p2_w = len(p2_df[wicket_mask_p2 & p2_df[dismissed_player_col].notna() & (p2_df[dismissed_player_col] != 'Unknown')])
                else:
                    p2_w = 0

                p1_balls = len(p1_df[(p1_df.get('extras_type', '') != 'wides') & (p1_df.get('extras_type', '') != 'noballs')])
                p2_balls = len(p2_df[(p2_df.get('extras_type', '') != 'wides') & (p2_df.get('extras_type', '') != 'noballs')])

                p1_overs = p1_balls / 6
                p2_overs = p2_balls / 6

                p1_runs = p1_df[~p1_df.get('extras_type', pd.Series()).isin(['byes', 'legbyes'])]['total_runs'].sum() if 'total_runs' in p1_df.columns else 0
                p2_runs = p2_df[~p2_df.get('extras_type', pd.Series()).isin(['byes', 'legbyes'])]['total_runs'].sum() if 'total_runs' in p2_df.columns else 0

                p1_econ = (p1_runs / p1_overs) if p1_overs > 0 else 0.0
                p2_econ = (p2_runs / p2_overs) if p2_overs > 0 else 0.0

                p1_matches = p1_df[match_id_col].nunique() if (match_id_col and match_id_col in p1_df.columns) else p1_df.shape[0]
                p2_matches = p2_df[match_id_col].nunique() if (match_id_col and match_id_col in p2_df.columns) else p2_df.shape[0]

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
                
                st.markdown("<div style='font-size: 1.1rem; font-weight: 700; color: #38bdf8; margin-bottom: 12px; margin-top: 15px;'>📈 Seasonal Wickets Progress</div>", unsafe_allow_html=True)
                if 'season' in deliveries.columns:
                    p1_w_mask = wicket_mask_p1 & p1_df['player_dismissed'].notna() & (p1_df['player_dismissed'] != 'Unknown')
                    p2_w_mask = wicket_mask_p2 & p2_df['player_dismissed'].notna() & (p2_df['player_dismissed'] != 'Unknown')
                    
                    p1_season = p1_df[p1_w_mask].groupby('season').size().reset_index(name='wickets')
                    p2_season = p2_df[p2_w_mask].groupby('season').size().reset_index(name='wickets')
                else:
                    merged_matches = _app.load_data()[0][['id', 'season']].rename(columns={'id': 'match_id'})
                    key = match_id_col or 'match_id'
                    if key in p1_df.columns:
                        p1_df = p1_df.merge(merged_matches, left_on=key, right_on='match_id', how='left')
                    if key in p2_df.columns:
                        p2_df = p2_df.merge(merged_matches, left_on=key, right_on='match_id', how='left')
                    if dismissal_col and dismissed_player_col:
                        p1_w_mask = p1_df[dismissal_col].str.lower().isin(_app.VALID_WICKET_KINDS) & p1_df[dismissed_player_col].notna() & (p1_df[dismissed_player_col] != 'Unknown')
                        p2_w_mask = p2_df[dismissal_col].str.lower().isin(_app.VALID_WICKET_KINDS) & p2_df[dismissed_player_col].notna() & (p2_df[dismissed_player_col] != 'Unknown')
                    else:
                        p1_w_mask = pd.Series(False, index=p1_df.index)
                        p2_w_mask = pd.Series(False, index=p2_df.index)
                    
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
            st.markdown(f"<div style='font-size: 1.25rem; font-weight: 800; color: #38bdf8; margin-bottom: 12px;'>🥊 Head-to-Head Duel: {selected_batsman} vs. {selected_bowler}</div>", unsafe_allow_html=True)
            
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
    render_header("VENUE INTELLIGENCE", "Identify high-scoring stadiums and analyze batting patterns by ground.")

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
    render_header("IPL MATCH PREDICTOR ENGINE", "Machine-assisted win probability calculations using historical matrices.")

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
        result = _app.compute_match_prediction(matches, team_a, team_b, venue, toss_winner, toss_decision)
        
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
    render_header("SMART FANTASY XI SELECTOR", "Algorithmic generation of optimal lineups based on player metrics and team strategies.")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        sel_season = st.selectbox("Select Season Pool", seasons, index=len(seasons)-1)
    with col_s2:
        strategy = st.selectbox("Select Team Strategy", ["Balanced XI", "Batting-Heavy XI", "Bowling-Heavy XI"])

    if 'season' in deliveries.columns:
        season_deliveries = deliveries[deliveries['season'] == sel_season]
    else:
        matches, _ = _app.load_data()
        cleaned_m = _app.clean_matches(matches)
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
                st.markdown(f"<div style='font-size: 1.25rem; font-weight: 800; color: #facc15; margin-bottom: 16px; border-left: 4px solid #facc15; padding-left: 10px;'>🌟 Optimal Fantasy Lineup - {strategy} ({sel_season})</div>", unsafe_allow_html=True)
                
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

# Note: UI rendering functions are defined above. No-op stubs removed to avoid overriding implementations.
