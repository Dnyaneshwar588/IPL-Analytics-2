import React, { useEffect, useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';
import { Target, HelpCircle, Trophy, BarChart2 } from 'lucide-react';

export default function Teams() {
  const [teams, setTeams] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState('');
  const [teamStats, setTeamStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchTeams() {
      try {
        const res = await fetch('/api/teams');
        const data = await res.json();
        setTeams(data);
        if (data.length > 0) {
          setSelectedTeam(data[0].name);
        }
      } catch (err) {
        console.error('Error fetching teams:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchTeams();
  }, []);

  useEffect(() => {
    if (selectedTeam) {
      const team = teams.find(t => t.name === selectedTeam);
      setTeamStats(team);
    }
  }, [selectedTeam, teams]);

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-accentBlue border-t-transparent"></div>
      </div>
    );
  }

  if (!teamStats) return null;

  // Prepare Pie Chart Data for Batting First vs Chasing Wins
  const winData = [
    { name: 'Defending (Bat First)', value: teamStats.battingFirstWins },
    { name: 'Chasing (Field First)', value: teamStats.chasingWins }
  ];

  // Prepare Toss Impact Data
  const tossData = [
    { name: 'Won Toss & Match', value: teamStats.tossMatchWins },
    { name: 'Lost Toss but Won Match', value: teamStats.wins - teamStats.tossMatchWins }
  ];

  // Prepare Season Trend Data
  const sortedSeasonStats = [...teamStats.seasonStats].sort((a, b) => parseInt(a.season) - parseInt(b.season));

  const COLORS = ['#38bdf8', '#fb923c'];
  const TOSS_COLORS = ['#10b981', '#a855f7'];

  return (
    <div className="space-y-8">
      {/* Header with Team Dropdown Selector */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white md:text-4xl">Franchise Performance Analysis</h1>
          <p className="mt-2 text-textMuted">Explore statistical insights and seasonal trends of each IPL team.</p>
        </div>
        <div>
          <select 
            value={selectedTeam}
            onChange={(e) => setSelectedTeam(e.target.value)}
            className="w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-white font-semibold outline-none focus:border-accentBlue sm:w-64"
          >
            {teams.map(t => (
              <option key={t.name} value={t.name}>{t.name}</option>
            ))}
          </select>
        </div>
      </div>

      {/* KPI row for selected team */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {/* KPI 1 */}
        <div className="glass-card p-6">
          <p className="text-xs font-semibold uppercase tracking-wider text-textMuted">Matches Played</p>
          <h3 className="mt-2 text-3xl font-extrabold text-white">{teamStats.matchesPlayed}</h3>
          <p className="mt-1 text-xs text-textMuted">Cumulative match counts</p>
        </div>

        {/* KPI 2 */}
        <div className="glass-card p-6">
          <p className="text-xs font-semibold uppercase tracking-wider text-textMuted">Total Wins</p>
          <h3 className="mt-2 text-3xl font-extrabold text-white">{teamStats.wins}</h3>
          <p className="mt-1 text-xs text-accentGreen font-semibold">Most wins at home & away</p>
        </div>

        {/* KPI 3 */}
        <div className="glass-card p-6">
          <p className="text-xs font-semibold uppercase tracking-wider text-textMuted">Win Rate</p>
          <h3 className="mt-2 text-3xl font-extrabold text-white">{teamStats.winPercentage}%</h3>
          <p className="mt-1 text-xs text-accentBlue font-semibold">Total Win / Play ratio</p>
        </div>

        {/* KPI 4 */}
        <div className="glass-card p-6">
          <p className="text-xs font-semibold uppercase tracking-wider text-textMuted">Toss Wins</p>
          <h3 className="mt-2 text-3xl font-extrabold text-white">{teamStats.tossWins}</h3>
          <p className="mt-1 text-xs text-accentYellow font-semibold">Toss win probability</p>
        </div>
      </div>

      {/* Double Column Graphs */}
      <div className="grid gap-8 lg:grid-cols-2">
        {/* Batting first vs Chasing Pie Chart */}
        <div className="glass-card p-6 space-y-4">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Target size={18} className="text-accentBlue" /> Win Conditions
            </h3>
            <p className="text-xs text-textMuted">Ratio of wins achieved when batting first vs chasing.</p>
          </div>
          <div className="h-64 flex justify-center items-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={winData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {winData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: 'rgba(255,255,255,0.08)', borderRadius: '10px' }} />
                <Legend verticalAlign="bottom" height={36} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Toss Win vs Match Win Pie Chart */}
        <div className="glass-card p-6 space-y-4">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <HelpCircle size={18} className="text-accentGreen" /> Toss Decision Impact
            </h3>
            <p className="text-xs text-textMuted">Analysis of wins that came after winning the toss.</p>
          </div>
          <div className="h-64 flex justify-center items-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={tossData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {tossData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={TOSS_COLORS[index % TOSS_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: 'rgba(255,255,255,0.08)', borderRadius: '10px' }} />
                <Legend verticalAlign="bottom" height={36} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Season Wise Trend Area Chart */}
      <div className="glass-card p-6 space-y-4">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <BarChart2 size={18} className="text-accentPurple" /> Season-wise Trend
          </h3>
          <p className="text-xs text-textMuted">Wins and Matches Played over the seasons.</p>
        </div>
        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={sortedSeasonStats}>
              <defs>
                <linearGradient id="colorWins" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#38bdf8" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorMatches" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#a855f7" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#a855f7" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="season" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0f172a', borderColor: 'rgba(255,255,255,0.08)', borderRadius: '10px' }}
                labelClassName="text-white font-bold"
              />
              <Legend />
              <Area type="monotone" dataKey="wins" name="Wins" stroke="#38bdf8" fillOpacity={1} fill="url(#colorWins)" />
              <Area type="monotone" dataKey="matchesPlayed" name="Matches Played" stroke="#a855f7" fillOpacity={1} fill="url(#colorMatches)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
