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
        <p className="mt-2 text-textMuted">Production-grade analytics platform powered by Machine Learning.</p>
        <div className="mt-4 h-1 w-20 rounded bg-gradient-to-r from-accentBlue to-accentPurple"></div>
      </div>

      {/* KPI Grid */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {/* KPI 1 */}
        <div className="glass-card p-6 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-textMuted">Total Matches</p>
            <h3 className="mt-2 text-3xl font-extrabold text-white">{stats.totalMatches}</h3>
            <p className="mt-1 text-xs text-accentGreen flex items-center gap-1 font-semibold">
              <Calendar size={12} /> 2008 - 2024 Seasons
            </p>
          </div>
          <div className="rounded-2xl bg-blue-500/10 p-4 text-accentBlue">
            <Activity size={28} />
          </div>
        </div>

        {/* KPI 2 */}
        <div className="glass-card p-6 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-textMuted">Avg 1st Inn Score</p>
            <h3 className="mt-2 text-3xl font-extrabold text-white">{stats.avgScore}</h3>
            <p className="mt-1 text-xs text-accentBlue flex items-center gap-1 font-semibold">
              <Zap size={12} /> Across All Grounds
            </p>
          </div>
          <div className="rounded-2xl bg-orange-500/10 p-4 text-accentOrange">
            <Zap size={28} />
          </div>
        </div>

        {/* KPI 3 */}
        <div className="glass-card p-6 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-textMuted">Top Franchise</p>
            <h3 className="mt-2 text-xl font-extrabold text-white truncate max-w-[180px]">{stats.mostSuccessfulTeam}</h3>
            <p className="mt-1 text-xs text-accentYellow flex items-center gap-1 font-semibold">
              <Trophy size={12} /> Most Wins in History
            </p>
          </div>
          <div className="rounded-2xl bg-yellow-500/10 p-4 text-accentYellow">
            <Trophy size={28} />
          </div>
        </div>

        {/* KPI 4 */}
        <div className="glass-card p-6 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-textMuted">All-Time Top Scorer</p>
            <h3 className="mt-2 text-xl font-extrabold text-white truncate max-w-[180px]">{stats.topScorer}</h3>
            <p className="mt-1 text-xs text-accentGreen flex items-center gap-1 font-semibold">
              <Award size={12} /> {stats.topScorerRuns} Career Runs
            </p>
          </div>
          <div className="rounded-2xl bg-emerald-500/10 p-4 text-accentGreen">
            <Users size={28} />
          </div>
        </div>
      </div>

      {/* Main Charts & Rankings Layout */}
      <div className="grid gap-8 lg:grid-cols-3">
        {/* Wins Chart (Span 2) */}
        <div className="glass-card p-6 lg:col-span-2 space-y-6">
          <div>
            <h3 className="text-lg font-bold text-white">Wins Distribution by Team</h3>
            <p className="text-xs text-textMuted">Franchise ranking based on historical match results.</p>
          </div>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={teamsData.slice(0, 10)}>
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickFormatter={(name) => name.split(' ').map(w => w[0]).join('')} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: 'rgba(255,255,255,0.08)', borderRadius: '10px' }}
                  labelClassName="text-white font-bold"
                  itemStyle={{ color: '#38bdf8' }}
                />
                <Bar dataKey="wins" radius={[6, 6, 0, 0]}>
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
            <p className="text-xs text-textMuted">Top performing batsman & bowler statistics.</p>
          </div>
          <div className="space-y-6">
            {/* Top Batsmen */}
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-textMuted mb-3">Top Batsmen (Runs)</h4>
              <div className="space-y-3">
                {topBatsmen.map((player, idx) => (
                  <div key={player.name} className="flex items-center justify-between p-2 rounded bg-slate-800/30 border border-slate-700/20">
                    <span className="text-sm font-semibold text-white">{idx+1}. {player.name}</span>
                    <span className="text-sm font-bold text-accentBlue">{player.battingStats.runs}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Top Bowlers */}
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-textMuted mb-3">Top Bowlers (Wickets)</h4>
              <div className="space-y-3">
                {topBowlers.map((player, idx) => (
                  <div key={player.name} className="flex items-center justify-between p-2 rounded bg-slate-800/30 border border-slate-700/20">
                    <span className="text-sm font-semibold text-white">{idx+1}. {player.name}</span>
                    <span className="text-sm font-bold text-accentGreen">{player.bowlingStats.wickets}</span>
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
