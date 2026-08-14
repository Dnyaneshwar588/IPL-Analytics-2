import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Award, Calendar, Activity, Zap, Users, MapPin, Award as Trophy } from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalMatches: 0,
    avgScore: 0,
    mostSuccessfulTeam: 'Loading...',
    topScorer: 'Loading...',
    topScorerRuns: 0
  });
  const [teamsData, setTeamsData] = useState([]);
  const [topBatsmen, setTopBatsmen] = useState([]);
  const [topBowlers, setTopBowlers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchDashboardData() {
      try {
        // Fetch teams
        const teamsRes = await fetch('/api/teams');
        const teams = await teamsRes.json();
        setTeamsData(teams);

        // Fetch players (top batsmen and bowlers)
        const playersBatRes = await fetch('/api/players?limit=5&sort=runs');
        const batPlayers = await playersBatRes.json();
        setTopBatsmen(batPlayers);

        const playersBowlRes = await fetch('/api/players?limit=5&sort=wickets');
        const bowlPlayers = await playersBowlRes.json();
        setTopBowlers(bowlPlayers);

        // Fetch venues for avg score calculation
        const venuesRes = await fetch('/api/venues');
        const venues = await venuesRes.json();

        // Calculate KPI values
        let totalMatches = 0;
        let totalRuns = 0;
        let venueCount = 0;

        venues.forEach(v => {
          totalMatches += v.matchesPlayed;
          if (v.avgFirstInningsScore > 0) {
            totalRuns += v.avgFirstInningsScore;
            venueCount++;
          }
        });

        const avgScore = venueCount > 0 ? Math.round(totalRuns / venueCount) : 160;
        const mostSuccessfulTeam = teams.length > 0 ? teams[0].name : 'Unknown';
        const topScorer = batPlayers.length > 0 ? batPlayers[0].name : 'Unknown';
        const topScorerRuns = batPlayers.length > 0 ? batPlayers[0].battingStats.runs : 0;

        setStats({
          totalMatches,
          avgScore,
          mostSuccessfulTeam,
          topScorer,
          topScorerRuns
        });
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchDashboardData();
  }, []);

  const COLORS = ['#38bdf8', '#3b82f6', '#10b981', '#a855f7', '#f97316', '#facc15'];

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-accentBlue border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-white md:text-4xl">IPL Pro Analytics Console</h1>
        <p className="mt-2 text-slate-400">Production-grade analytics platform powered by Machine Learning.</p>
        <div className="mt-4 h-1 w-20 rounded bg-gradient-to-r from-accentBlue to-accentPurple" aria-hidden="true"></div>
      </div>

      {/* KPI Grid */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {/* KPI 1 - Total Matches */}
        <div className="kpi-card">
          <div className="flex items-start justify-between mb-4">
            <div className="rounded-xl bg-accentBlue/20 p-3 text-accentBlue">
              <Activity size={24} />
            </div>
          </div>
          <p className="form-label">Total Matches</p>
          <h3 className="mt-2 text-4xl font-extrabold gradient-text">{stats.totalMatches}</h3>
          <p className="mt-3 text-xs text-slate-400 flex items-center gap-1 font-medium">
            <Calendar size={14} className="text-accentBlue" /> 2008 - 2024 Seasons
          </p>
        </div>

        {/* KPI 2 - Avg 1st Inn Score (Highlight) */}
        <div className="kpi-card highlight lg:col-span-1">
          <div className="flex items-start justify-between mb-4">
            <div className="rounded-xl bg-accentOrange/20 p-3 text-accentOrange">
              <Zap size={24} />
            </div>
          </div>
          <p className="form-label">Avg 1st Inn Score</p>
          <h3 className="mt-2 text-4xl font-extrabold gradient-orange-text">{stats.avgScore}</h3>
          <p className="mt-3 text-xs text-slate-400 flex items-center gap-1 font-medium">
            <Zap size={14} className="text-accentOrange" /> Across All Grounds
          </p>
        </div>

        {/* KPI 3 - Top Franchise (Highlight) */}
        <div className="kpi-card highlight">
          <div className="flex items-start justify-between mb-4">
            <div className="rounded-xl bg-accentYellow/20 p-3 text-accentYellow">
              <Trophy size={24} />
            </div>
          </div>
          <p className="form-label">Top Franchise</p>
          <h3 className="mt-2 text-2xl font-extrabold text-white line-clamp-1">{stats.mostSuccessfulTeam}</h3>
          <p className="mt-3 text-xs text-slate-400 flex items-center gap-1 font-medium">
            <Trophy size={14} className="text-accentYellow" /> Most Wins in History
          </p>
        </div>

        {/* KPI 4 - Top Scorer */}
        <div className="kpi-card">
          <div className="flex items-start justify-between mb-4">
            <div className="rounded-xl bg-accentGreen/20 p-3 text-accentGreen">
              <Users size={24} />
            </div>
          </div>
          <p className="form-label">All-Time Top Scorer</p>
          <h3 className="mt-2 text-2xl font-extrabold text-white line-clamp-1">{stats.topScorer}</h3>
          <p className="mt-3 text-xs text-slate-400 flex items-center gap-1 font-medium">
            <Award size={14} className="text-accentGreen" /> {stats.topScorerRuns} Career Runs
          </p>
        </div>
      </div>

      {/* Main Charts & Rankings Layout */}
      <div className="grid gap-8 lg:grid-cols-3">
        {/* Wins Chart (Span 2) */}
        <div className="glass-card p-6 lg:col-span-2 space-y-6">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Trophy size={20} className="text-accentYellow" />
              Wins Distribution by Team
            </h3>
            <p className="text-xs text-slate-400 mt-1">Franchise ranking based on historical match results.</p>
          </div>
          <div className="h-80 w-full rounded-lg overflow-hidden bg-slate-900/30 p-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={teamsData.slice(0, 10)} margin={{ top: 10, right: 20, left: 0, bottom: 30 }}>
                <XAxis 
                  dataKey="name" 
                  stroke="#64748b" 
                  fontSize={12}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                  tick={{ fill: '#94a3b8', fontWeight: 500 }}
                />
                <YAxis stroke="#64748b" fontSize={12} tick={{ fill: '#94a3b8' }} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1e293b', 
                    borderColor: '#38bdf8',
                    borderRadius: '10px',
                    boxShadow: '0 10px 25px rgba(0,0,0,0.3)'
                  }}
                  labelClassName="text-white font-bold text-sm"
                  labelStyle={{ color: '#f1f5f9' }}
                  itemStyle={{ color: '#38bdf8', fontWeight: 600 }}
                  formatter={(value) => [`${value} wins`, 'Total']}
                  cursor={{ fill: 'rgba(56, 189, 248, 0.1)' }}
                />
                <Bar dataKey="wins" radius={[8, 8, 0, 0]} isAnimationActive={true}>
                  {teamsData.slice(0, 10).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Leaderboards (Span 1) */}
        <div className="glass-card p-6 space-y-6">
          <div>
            <h3 className="text-lg font-bold text-white">League Leaders</h3>
            <p className="text-xs text-textMuted mt-1">Top performing batsman & bowler statistics.</p>
          </div>
          <div className="space-y-6">
            {/* Top Batsmen */}
            <div>
              <h4 className="form-label mb-3">Top Batsmen (Runs)</h4>
              <div className="space-y-2">
                {topBatsmen.map((player, idx) => (
                  <div key={player.name} className="leaderboard-item">
                    <div className="leaderboard-rank">
                      #{idx + 1}
                    </div>
                    <div className="leaderboard-info">
                      <p className="text-sm font-semibold text-white line-clamp-1">{player.name}</p>
                      <p className="text-xs text-slate-400">Batsman</p>
                    </div>
                    <div className="leaderboard-value">
                      <p className="text-base font-extrabold gradient-text">{player.battingStats.runs}</p>
                      <p className="text-xs text-slate-400">runs</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Top Bowlers */}
            <div>
              <h4 className="form-label mb-3">Top Bowlers (Wickets)</h4>
              <div className="space-y-2">
                {topBowlers.map((player, idx) => (
                  <div key={player.name} className="leaderboard-item">
                    <div className="leaderboard-rank">
                      #{idx + 1}
                    </div>
                    <div className="leaderboard-info">
                      <p className="text-sm font-semibold text-white line-clamp-1">{player.name}</p>
                      <p className="text-xs text-slate-400">Bowler</p>
                    </div>
                    <div className="leaderboard-value">
                      <p className="text-base font-extrabold gradient-green-text">{player.bowlingStats.wickets}</p>
                      <p className="text-xs text-slate-400">wickets</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
