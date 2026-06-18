import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Zap, HelpCircle, AlertCircle, RefreshCw } from 'lucide-react';

export default function Predictor() {
  const [teams, setTeams] = useState([]);
  const [venues, setVenues] = useState([]);

  // Form states
  const [teamA, setTeamA] = useState('');
  const [teamB, setTeamB] = useState('');
  const [venue, setVenue] = useState('');
  const [tossWinner, setTossWinner] = useState('');
  const [tossDecision, setTossDecision] = useState('field');

  // Prediction states
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadData() {
      try {
        const teamsRes = await fetch('/api/teams');
        const teamsList = await teamsRes.json();
        setTeams(teamsList);
        if (teamsList.length > 0) {
          setTeamA(teamsList[0].name);
          setTeamB(teamsList[1]?.name || teamsList[0].name);
          setTossWinner(teamsList[0].name);
        }

        const venuesRes = await fetch('/api/venues');
        const venuesList = await venuesRes.json();
        setVenues(venuesList);
        if (venuesList.length > 0) {
          setVenue(venuesList[0].venue);
        }
      } catch (err) {
        console.error('Error fetching list data:', err);
      }
    }
    loadData();
  }, []);

  // Update toss winner options when Team A or Team B changes
  const handleTeamAChange = (val) => {
    setTeamA(val);
    if (tossWinner !== val && tossWinner !== teamB) {
      setTossWinner(val);
    }
  };

  const handleTeamBChange = (val) => {
    setTeamB(val);
    if (tossWinner !== teamA && tossWinner !== val) {
      setTossWinner(val);
    }
  };

  const executePrediction = async (e) => {
    e.preventDefault();
    if (teamA === teamB) {
      setError('Please select two different teams.');
      return;
    }
    setError('');
    setLoading(true);
    setPrediction(null);

    try {
      const res = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          team1: teamA,
          team2: teamB,
          venue,
          tossWinner,
          tossDecision,
          season: '2024'
        })
      });
      const data = await res.json();
      if (res.ok) {
        setPrediction(data);
      } else {
        setError(data.details?.detail || 'Inference engine is starting up. Please try again shortly.');
      }
    } catch (err) {
      setError('Could not connect to the ML Service.');
    } finally {
      setLoading(false);
    }
  };

  // Prepare chart data for factor breakdown
  let breakdownData = [];
  if (prediction?.factor_breakdown) {
    breakdownData = Object.keys(prediction.factor_breakdown).map((key) => ({
      factor: key,
      value: prediction.factor_breakdown[key]
    }));
  }

  const COLORS = ['#38bdf8', '#3b82f6', '#10b981', '#a855f7'];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-white md:text-4xl">ML Match Predictor</h1>
        <p className="mt-2 text-textMuted">Harness XGBoost models to simulate matches and predict win probabilities.</p>
        <div className="mt-4 h-1 w-20 rounded bg-gradient-to-r from-accentBlue to-accentPurple"></div>
      </div>

      {/* Main Layout */}
      <div className="grid gap-8 lg:grid-cols-3">
        {/* Predictor Form */}
        <div className="glass-card p-6 h-fit space-y-6">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Zap size={18} className="text-accentBlue" /> Simulation Console
          </h3>

          <form onSubmit={executePrediction} className="space-y-4">
            {/* Team A Selection */}
            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold text-textMuted uppercase tracking-wider">Team A</label>
              <select
                value={teamA}
                onChange={(e) => handleTeamAChange(e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-2.5 text-sm text-white font-semibold outline-none focus:border-accentBlue"
              >
                {teams.map(t => (
                  <option key={t.name} value={t.name}>{t.name}</option>
                ))}
              </select>
            </div>

            {/* Team B Selection */}
            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold text-textMuted uppercase tracking-wider">Team B</label>
              <select
                value={teamB}
                onChange={(e) => handleTeamBChange(e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-2.5 text-sm text-white font-semibold outline-none focus:border-accentBlue"
              >
                {teams.map(t => (
                  <option key={t.name} value={t.name}>{t.name}</option>
                ))}
              </select>
            </div>

            {/* Venue Selection */}
            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold text-textMuted uppercase tracking-wider">Venue</label>
              <select
                value={venue}
                onChange={(e) => setVenue(e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-2.5 text-sm text-white font-semibold outline-none focus:border-accentBlue"
              >
                {venues.map(v => (
                  <option key={v.venue} value={v.venue}>{v.venue}</option>
                ))}
              </select>
            </div>

            {/* Toss Winner Selection */}
            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold text-textMuted uppercase tracking-wider">Toss Winner</label>
              <select
                value={tossWinner}
                onChange={(e) => setTossWinner(e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-2.5 text-sm text-white font-semibold outline-none focus:border-accentBlue"
              >
                <option value={teamA}>{teamA}</option>
                <option value={teamB}>{teamB}</option>
              </select>
            </div>

            {/* Toss Decision Selection */}
            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold text-textMuted uppercase tracking-wider">Toss Decision</label>
              <select
                value={tossDecision}
                onChange={(e) => setTossDecision(e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-2.5 text-sm text-white font-semibold outline-none focus:border-accentBlue"
              >
                <option value="field">Field First (Chasing)</option>
                <option value="bat">Bat First (Defending)</option>
              </select>
            </div>

            {/* Error Message */}
            {error && (
              <div className="rounded-xl bg-red-500/10 border border-red-500/20 p-3 text-red-400 text-xs flex items-center gap-2">
                <AlertCircle size={14} className="shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-accentBlue to-accentPurple font-extrabold text-white text-sm hover:opacity-95 disabled:opacity-40 transition-all flex justify-center items-center gap-2"
            >
              {loading ? (
                <>
                  <RefreshCw className="animate-spin" size={16} /> Run Simulation
                </>
              ) : (
                'Run Simulation'
              )}
            </button>
          </form>
        </div>

        {/* Prediction Results Panel (Span 2) */}
        <div className="lg:col-span-2 space-y-6">
          {prediction ? (
            <div className="glass-card p-6 space-y-8 animate-fade-in">
              {/* Win Probabilities Bar */}
              <div className="space-y-4">
                <h3 className="text-lg font-bold text-white">Win Probabilities</h3>
                <div className="w-full bg-slate-900 rounded-full h-10 overflow-hidden flex border border-slate-800 shadow-inner">
                  <div 
                    className="bg-gradient-to-r from-accentBlue to-blue-600 h-full flex items-center justify-center text-xs font-black text-white px-4 transition-all duration-1000"
                    style={{ width: `${prediction.team1_probability}%` }}
                  >
                    {prediction.team1_probability}%
                  </div>
                  <div 
                    className="bg-gradient-to-r from-orange-500 to-accentOrange h-full flex items-center justify-center text-xs font-black text-white px-4 transition-all duration-1000"
                    style={{ width: `${prediction.team2_probability}%` }}
                  >
                    {prediction.team2_probability}%
                  </div>
                </div>
                <div className="flex items-center justify-between text-xs text-textMuted font-bold px-1">
                  <span>{prediction.team1}</span>
                  <span>{prediction.team2}</span>
                </div>
              </div>

              {/* Confidence & Details */}
              <div className="grid gap-6 sm:grid-cols-2">
                <div className="p-4 bg-slate-800/20 border border-slate-700/20 rounded-2xl">
                  <p className="text-xs text-textMuted uppercase font-bold tracking-wider">Model Confidence</p>
                  <p className="mt-2 text-3xl font-black text-white">{prediction.confidence}%</p>
                  <p className="mt-1 text-[10px] text-textMuted">Predictive margin of certainty.</p>
                </div>
                <div className="p-4 bg-slate-800/20 border border-slate-700/20 rounded-2xl space-y-1 text-sm">
                  <p className="text-xs text-textMuted uppercase font-bold tracking-wider mb-2">Historical H2H Records</p>
                  <div className="flex justify-between">
                    <span className="text-textMuted">Matches Played:</span>
                    <span className="text-white font-bold">{prediction.details.h2h_played}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-textMuted">Wins for {prediction.team1}:</span>
                    <span className="text-accentBlue font-bold">{prediction.details.h2h_wins_team1}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-textMuted">Wins for {prediction.team2}:</span>
                    <span className="text-accentOrange font-bold">{prediction.details.h2h_wins_team2}</span>
                  </div>
                </div>
              </div>

              {/* Factors Breakdown */}
              <div className="space-y-4">
                <div>
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <HelpCircle size={16} className="text-accentPurple" /> Model Decision Breakdown
                  </h3>
                  <p className="text-xs text-textMuted mt-1">Relative contribution of variables to the final winner prediction.</p>
                </div>
                <div className="h-60 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={breakdownData} layout="vertical">
                      <XAxis type="number" stroke="#64748b" fontSize={11} domain={[0, 100]} />
                      <YAxis type="category" dataKey="factor" stroke="#64748b" fontSize={11} width={100} />
                      <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: 'rgba(255,255,255,0.08)', borderRadius: '10px' }} />
                      <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                        {breakdownData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          ) : (
            <div className="glass-card p-12 text-center flex flex-col items-center justify-center h-full border-dashed">
              <div className="p-4 bg-slate-900 rounded-full text-slate-700 mb-4">
                <Zap size={40} />
              </div>
              <h3 className="text-lg font-bold text-white">Simulation Panel Offline</h3>
              <p className="text-sm text-textMuted mt-2 max-w-sm">Configure simulation criteria in the sidebar and trigger predictive inference.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
