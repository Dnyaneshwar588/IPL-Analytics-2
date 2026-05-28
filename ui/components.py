import streamlit as st
import pandas as pd
import html as _html
from typing import Optional

def kpi_card(title: str, value: str, subtitle: Optional[str] = None, icon: str = "🏏") -> None:
        # Escape any user-provided text to avoid accidental HTML rendering
        safe_title = _html.escape(str(title))
        safe_value = _html.escape(str(value))
        safe_sub = _html.escape(str(subtitle)) if subtitle is not None else None

        inner = (
                f"<div style=\"display:flex;align-items:center;gap:16px;\">"
                f"<div style=\"width:52px;height:52px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:24px;background:linear-gradient(135deg,#0ea5e9,#6366f1);box-shadow:0 6px 18px rgba(2,6,23,0.35);flex-shrink:0;\">"
                f"<span style=\"font-size:22px\">{_html.escape(icon)}</span>"
                f"</div>"
                f"<div style=\"flex:1;\">"
                f"<div style=\"font-size:12px;color:#94a3b8;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;\">{safe_title}</div>"
                f"<div style=\"font-size:24px;font-weight:800;color:#ffffff;margin-top:2px;\">{safe_value}</div>"
        )
        if safe_sub:
                inner += f"<div style=\"font-size:11px;color:#64748b;margin-top:3px;font-weight:500;\">{safe_sub}</div>"
        inner += "</div>"

        wrapper = f"<div class='custom-kpi-card'>{inner}</div>"
        st.markdown(wrapper, unsafe_allow_html=True)



@st.cache_data
def compute_insights(matches: pd.DataFrame, deliveries: pd.DataFrame) -> dict:
    insights = {}
    try:
        if not matches.empty:
            # Best performing team by wins
            wins = matches['winner'].dropna().value_counts()
            insights['best_team'] = wins.idxmax() if not wins.empty else None
            insights['best_team_wins'] = int(wins.max()) if not wins.empty else 0

            # Toss impact: percent of matches where toss_winner == winner
            if {'toss_winner', 'winner'}.issubset(matches.columns):
                toss_df = matches.assign(toss_win=matches['toss_winner'] == matches['winner'])
                toss_rate = toss_df['toss_win'].mean() * 100
                insights['toss_win_pct'] = round(toss_rate, 2)
            else:
                insights['toss_win_pct'] = None

            # Venue advantage: venues with biggest chasing vs defending delta
            if {'venue', 'win_by_runs', 'win_by_wickets', 'winner'}.issubset(matches.columns):
                venue_stats = {}
                for v, g in matches.groupby('venue'):
                    bat_first = len(g[g['win_by_runs'] > 0])
                    chase = len(g[g['win_by_wickets'] > 0])
                    venue_stats[v] = {'bat_first': int(bat_first), 'chase': int(chase)}
                insights['venue_stats'] = venue_stats
            else:
                insights['venue_stats'] = {}

        if not deliveries.empty:
            # Top consistent players: players with most appearances across matches and seasons
            batter_col = None
            for c in ['batsman', 'striker', 'batter']:
                if c in deliveries.columns:
                    batter_col = c
                    break
            if batter_col:
                top_bat = deliveries.groupby(batter_col).size().sort_values(ascending=False).head(5)
                insights['top_consistent_batters'] = top_bat.index.tolist()
            else:
                insights['top_consistent_batters'] = []

    except Exception:
        pass
    return insights
