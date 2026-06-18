import React, { useEffect, useState } from 'react';
import { Sparkles, HelpCircle, Award, ShieldAlert, AlertCircle } from 'lucide-react';

export default function FantasyXI() {
  const [teams, setTeams] = useState([]);
  const [venues, setVenues] = useState([]);

  // Form states
  const [teamA, setTeamA] = useState('');
  const [teamB, setTeamB] = useState('');
  const [venue, setVenue] = useState('');
  const [strategy, setStrategy] = useState('Balanced XI');

  // Recommendation states
  const [lineup, setLineup] = useState(null);
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

  const buildFantasyTeam = async (e) => {
    e.preventDefault();
    if (teamA === teamB) {
      setError('Please select two different teams.');
      return;
    }
    setError('');
    setLoading(true);
    setLineup(null);

    try {
      const res = await fetch('/api/fantasy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          team1: teamA,
          team2: teamB,
          venue,
          strategy
        })
      });
      const data = await res.json();
      if (res.ok) {
        setLineup(data);
      } else {
        setError('Inference engine is starting up. Please try again shortly.');
      }
    } catch (err) {
      setError('Could not connect to the Express / ML API.');
    } finally {
      setLoading(false);
    }
  };

  // Role style helpers
  function getRoleBadge(role) {
    if (role === 'Wicketkeeper') return 'bg-yellow-500/10 text-accentYellow border border-yellow-500/20';
    if (role === 'Batsman') return 'bg-blue-500/10 text-accentBlue border border-blue-500/20';
    if (role === 'All-Rounder') return 'bg-purple-500/10 text-accentPurple border border-purple-500/20';
    return 'bg-emerald-500/10 text-accentGreen border border-emerald-500/20'; // Bowler
  }

  function getRoleShort(role) {
    if (role === 'Wicketkeeper') return 'WK';
    if (role === 'Batsman') return 'BAT';
    if (role === 'All-Rounder') return 'AR';
    return 'BOWL';
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-white md:text-4xl">Smart Fantasy XI</h1>
        <p className="mt-2 text-textMuted">Build optimal fantasy playing XIs using Gradient Boosting player predictions.</p>
        <div className="mt-4 h-1 w-20 rounded bg-gradient-to-r from-accentBlue to-accentPurple"></div>
      </div>

      {/* Main Layout */}
      <div className="grid gap-8 lg:grid-cols-4">
        {/* Selection panel */}
        <div className="glass-card p-6 h-fit space-y-6">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Sparkles size={18} className="text-accentPurple" /> Team Generator
          </h3>

          <form onSubmit={buildFantasyTeam} className="space-y-4">
            {/* Team A Selection */}
            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold text-textMuted uppercase tracking-wider">Team A</label>
              <select
                value={teamA}
                onChange={(e) => setTeamA(e.target.value)}
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
                onChange={(e) => setTeamB(e.target.value)}
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

            {/* Strategy Selection */}
            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold text-textMuted uppercase tracking-wider">Squad Strategy</label>
              <select
                value={strategy}
                onChange={(e) => setStrategy(e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-2.5 text-sm text-white font-semibold outline-none focus:border-accentBlue"
              >
                <option value="Balanced XI">Balanced XI</option>
                <option value="Batting-Heavy XI">Batting-Heavy XI</option>
                <option value="Bowling-Heavy XI">Bowling-Heavy XI</option>
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
              className="w-full py-3 rounded-xl bg-gradient-to-r from-accentBlue to-accentPurple font-extrabold text-white text-sm hover:opacity-95 disabled:opacity-40 transition-all"
            >
              {loading ? 'Generating...' : 'Assemble XI'}
            </button>
          </form>
        </div>

        {/* playing XI lineup (Span 3) */}
        <div className="lg:col-span-3 space-y-6">
          {lineup ? (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Award size={18} className="text-accentYellow" /> Recommended Playing XI
                </h3>
                <span className="text-[10px] font-bold tracking-wider uppercase bg-purple-500/10 text-accentPurple px-3 py-1.5 rounded-full border border-purple-500/20">
                  {strategy}
                </span>
              </div>

              {/* Player Badges Grid */}
              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
                {lineup.map((player) => {
                  let borderStyle = 'border-slate-800';
                  if (player.isCaptain) borderStyle = 'border-accentYellow shadow-lg shadow-yellow-500/5 ring-1 ring-accentYellow/20';
                  if (player.isViceCaptain) borderStyle = 'border-accentBlue shadow-lg shadow-blue-500/5 ring-1 ring-accentBlue/20';

                  return (
                    <div 
                      key={player.name}
                      className={`glass-card p-5 border flex flex-col justify-between hover:translate-y-[-2px] ${borderStyle}`}
                    >
                      {/* Top Header Row of Card */}
                      <div className="flex justify-between items-start gap-2">
                        <div>
                          {player.isCaptain && (
                            <span className="text-[9px] font-black uppercase bg-accentYellow text-darkBg px-2 py-0.5 rounded-md mr-1.5">
                              C (2x)
                            </span>
                          )}
                          {player.isViceCaptain && (
                            <span className="text-[9px] font-black uppercase bg-accentBlue text-darkBg px-2 py-0.5 rounded-md mr-1.5">
                              VC (1.5x)
                            </span>
                          )}
                          <h4 className="text-sm font-extrabold text-white truncate max-w-[140px] mt-1">{player.name}</h4>
                        </div>
                        <span className={`text-[10px] font-black px-2 py-0.5 rounded ${getRoleBadge(player.role)}`}>
                          {getRoleShort(player.role)}
                        </span>
                      </div>

                      {/* Score metric */}
                      <div className="mt-4 pt-3 border-t border-slate-800/40 flex justify-between items-center text-xs">
                        <span className="text-textMuted font-bold">Predicted Points</span>
                        <span className="text-base font-black text-white">{player.predicted_points}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            <div className="glass-card p-12 text-center flex flex-col items-center justify-center h-full border-dashed">
              <div className="p-4 bg-slate-900 rounded-full text-slate-700 mb-4">
                <Sparkles size={40} />
              </div>
              <h3 className="text-lg font-bold text-white">Lineup Draft Area</h3>
              <p className="text-sm text-textMuted mt-2 max-w-sm">Choose team context and strategy preferences to build a playing XI recommended by our models.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
