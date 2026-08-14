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
      <div className="flex flex-col gap-6 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white md:text-4xl">Franchise Performance Analysis</h1>
          <p className="mt-2 text-slate-400">Explore statistical insights and seasonal trends of each IPL team.</p>
        </div>
        <div className="w-full sm:w-64">
          <label className="form-label block mb-2">Select Team</label>
          <select 
            value={selectedTeam}
            onChange={(e) => setSelectedTeam(e.target.value)}
            className="form-select w-full"
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
        <div className="kpi-card">
          <div className="rounded-lg bg-accentBlue/20 p-3 text-accentBlue w-fit mb-3">
            <Trophy size={20} />
          </div>
          <p className="form-label">Matches Played</p>
          <h3 className="mt-2 text-4xl font-extrabold gradient-text">{teamStats.matchesPlayed}</h3>
          <p className="mt-3 text-xs text-slate-400">Cumulative match counts</p>
        </div>

        {/* KPI 2 - Highlight */}
        <div className="kpi-card highlight">
          <div className="rounded-lg bg-accentGreen/20 p-3 text-accentGreen w-fit mb-3">
            <Trophy size={20} />
          </div>
          <p className="form-label">Total Wins</p>
          <h3 className="mt-2 text-4xl font-extrabold gradient-green-text">{teamStats.wins}</h3>
          <p className="mt-3 text-xs text-slate-400">Most wins at home & away</p>
        </div>

        {/* KPI 3 */}
        <div className="kpi-card">
          <div className="rounded-lg bg-accentBlue/20 p-3 text-accentBlue w-fit mb-3">
            <BarChart2 size={20} />
          </div>
          <p className="form-label">Win Rate</p>
          <h3 className="mt-2 text-4xl font-extrabold text-white">{teamStats.winPercentage}%</h3>
          <p className="mt-3 text-xs text-slate-400">Total Win / Play ratio</p>
        </div>

        {/* KPI 4 */}
        <div className="kpi-card">
          <div className="rounded-lg bg-accentYellow/20 p-3 text-accentYellow w-fit mb-3">
            <Target size={20} />
          </div>
          <p className="form-label">Toss Wins</p>
          <h3 className="mt-2 text-4xl font-extrabold text-white">{teamStats.tossWins}</h3>
          <p className="mt-3 text-xs text-slate-400">Toss win probability</p>
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
            <p className="text-xs text-slate-400 mt-1">Ratio of wins achieved when batting first vs chasing.</p>
          </div>
          <div className="h-72 flex justify-center items-center rounded-lg bg-slate-900/30 p-4">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={winData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, value, percent }) => `${name}: ${value} (${(percent * 100).toFixed(0)}%)`}
                  labelLine={false}
                >
                  {winData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1e293b', 
                    borderColor: '#38bdf8',
                    borderRadius: '8px',
                    boxShadow: '0 10px 25px rgba(0,0,0,0.3)'
                  }}
                  formatter={(value) => [`${value} wins`, 'Count']}
                />
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
            <p className="text-xs text-slate-400 mt-1">Analysis of wins that came after winning the toss.</p>
          </div>
          <div className="h-72 flex justify-center items-center rounded-lg bg-slate-900/30 p-4">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={tossData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, value, percent }) => `${name}: ${value} (${(percent * 100).toFixed(0)}%)`}
                  labelLine={false}
                >
                  {tossData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={TOSS_COLORS[index % TOSS_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1e293b', 
                    borderColor: '#10b981',
                    borderRadius: '8px',
                    boxShadow: '0 10px 25px rgba(0,0,0,0.3)'
                  }}
                  formatter={(value) => [`${value} wins`, 'Count']}
                />
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
          <p className="text-xs text-slate-400 mt-1">Wins and Matches Played over the seasons.</p>
        </div>
        <div className="h-80 w-full rounded-lg overflow-hidden bg-slate-900/30 p-4">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={sortedSeasonStats} margin={{ top: 10, right: 30, left: 0, bottom: 30 }}>
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
              <XAxis 
                dataKey="season" 
                stroke="#64748b" 
                fontSize={12}
                tick={{ fill: '#94a3b8', fontWeight: 500 }}
              />
              <YAxis 
                stroke="#64748b" 
                fontSize={12}
                tick={{ fill: '#94a3b8' }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1e293b', 
                  borderColor: '#38bdf8',
                  borderRadius: '8px',
                  boxShadow: '0 10px 25px rgba(0,0,0,0.3)'
                }}
                labelStyle={{ color: '#f1f5f9', fontWeight: 600 }}
                cursor={{ fill: 'rgba(56, 189, 248, 0.1)' }}
              />
              <Legend 
                wrapperStyle={{ paddingTop: '20px' }}
                itemStyle={{ color: '#cbd5e1', fontSize: '12px', fontWeight: 500 }}
              />
              <Area 
                type="monotone" 
                dataKey="wins" 
                name="Wins" 
                stroke="#38bdf8" 
                strokeWidth={2}
                fillOpacity={1} 
                fill="url(#colorWins)"
                isAnimationActive={true}
              />
              <Area 
                type="monotone" 
                dataKey="matchesPlayed" 
                name="Matches Played" 
                stroke="#a855f7" 
                strokeWidth={2}
                fillOpacity={1} 
                fill="url(#colorMatches)"
                isAnimationActive={true}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
