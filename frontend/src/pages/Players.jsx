import React, { useEffect, useState } from 'react';
import { Search, Flame, Shield, X, User } from 'lucide-react';

export default function Players() {
  const [topBatsmen, setTopBatsmen] = useState([]);
  const [topBowlers, setTopBowlers] = useState([]);
  const [loading, setLoading] = useState(true);

  // Matchup Modal States
  const [showModal, setShowModal] = useState(false);
  const [searchBatter, setSearchBatter] = useState('');
  const [searchBowler, setSearchBowler] = useState('');
  const [batterResults, setBatterResults] = useState([]);
  const [bowlerResults, setBowlerResults] = useState([]);
  
  const [selectedBatter, setSelectedBatter] = useState('');
  const [selectedBowler, setSelectedBowler] = useState('');
  const [matchupData, setMatchupData] = useState(null);
  const [matchupLoading, setMatchupLoading] = useState(false);

  useEffect(() => {
    async function fetchLeaderboards() {
      try {
        const batRes = await fetch('/api/players?limit=10&sort=runs');
        const batData = await batRes.json();
        setTopBatsmen(batData);

        const bowlRes = await fetch('/api/players?limit=10&sort=wickets');
        const bowlData = await bowlRes.json();
        setTopBowlers(bowlData);
      } catch (err) {
        console.error('Error fetching leaderboards:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchLeaderboards();
  }, []);

  // Batter search handler
  useEffect(() => {
    if (searchBatter.trim().length > 1) {
      fetch(`/api/players?search=${searchBatter}&limit=5&role=Batsman`)
        .then(res => res.json())
        .then(data => setBatterResults(data))
        .catch(err => console.error(err));
    } else {
      setBatterResults([]);
    }
  }, [searchBatter]);

  // Bowler search handler
  useEffect(() => {
    if (searchBowler.trim().length > 1) {
      fetch(`/api/players?search=${searchBowler}&limit=5&role=Bowler`)
        .then(res => res.json())
        .then(data => setBowlerResults(data))
        .catch(err => console.error(err));
    } else {
      setBowlerResults([]);
    }
  }, [searchBowler]);

  // Fetch matchup head-to-head
  async function getMatchup() {
    if (!selectedBatter || !selectedBowler) return;
    setMatchupLoading(true);
    setMatchupData(null);
    try {
      const res = await fetch(`/api/matchup?batsman=${encodeURIComponent(selectedBatter)}&bowler=${encodeURIComponent(selectedBowler)}`);
      const data = await res.json();
      setMatchupData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setMatchupLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-accentBlue border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header with Matchup Button */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white md:text-4xl">Player Leaderboards</h1>
          <p className="mt-2 text-textMuted">Explore historical batting and bowling achievements of players.</p>
        </div>
        <div>
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-accentBlue to-accentPurple px-6 py-3 text-sm font-extrabold text-white shadow-lg shadow-blue-500/20 hover:scale-[1.03] transition-all"
          >
            <Flame size={16} /> Batter vs Bowler Matchup
          </button>
        </div>
      </div>

      {/* Leaderboards Grid */}
      <div className="grid gap-8 lg:grid-cols-2">
        {/* Top 10 Batsmen */}
        <div className="glass-card p-6 space-y-4">
          <div className="flex items-center gap-2">
            <Flame size={20} className="text-accentBlue" />
            <h3 className="text-lg font-bold text-white">Top 10 Batsmen</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-xs font-semibold uppercase tracking-wider text-textMuted">
                  <th className="py-3 pr-4">Player</th>
                  <th className="py-3 px-4 text-center">Runs</th>
                  <th className="py-3 px-4 text-center">Avg</th>
                  <th className="py-3 px-4 text-center">SR</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/40">
                {topBatsmen.map((player) => (
                  <tr key={player.name} className="hover:bg-slate-800/20 text-sm">
                    <td className="py-3 pr-4 font-semibold text-white">{player.name}</td>
                    <td className="py-3 px-4 text-center font-bold text-accentBlue">{player.battingStats.runs}</td>
                    <td className="py-3 px-4 text-center text-textMain">{player.battingStats.average}</td>
                    <td className="py-3 px-4 text-center text-textMuted">{player.battingStats.strikeRate}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Top 10 Bowlers */}
        <div className="glass-card p-6 space-y-4">
          <div className="flex items-center gap-2">
            <Shield size={20} className="text-accentGreen" />
            <h3 className="text-lg font-bold text-white">Top 10 Bowlers</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-xs font-semibold uppercase tracking-wider text-textMuted">
                  <th className="py-3 pr-4">Player</th>
                  <th className="py-3 px-4 text-center">Wickets</th>
                  <th className="py-3 px-4 text-center">Econ</th>
                  <th className="py-3 px-4 text-center">Avg</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/40">
                {topBowlers.map((player) => (
                  <tr key={player.name} className="hover:bg-slate-800/20 text-sm">
                    <td className="py-3 pr-4 font-semibold text-white">{player.name}</td>
                    <td className="py-3 px-4 text-center font-bold text-accentGreen">{player.bowlingStats.wickets}</td>
                    <td className="py-3 px-4 text-center text-textMain">{player.bowlingStats.economy}</td>
                    <td className="py-3 px-4 text-center text-textMuted">{player.bowlingStats.average}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Matchup Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="glass-card w-full max-w-2xl overflow-hidden relative p-6 max-h-[90vh] flex flex-col">
            {/* Modal Header */}
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Flame size={20} className="text-accentBlue" /> Head-to-Head Duel Creator
              </h3>
              <button onClick={() => { setShowModal(false); setMatchupData(null); }} className="text-textMuted hover:text-white">
                <X size={20} />
              </button>
            </div>

            {/* Modal Body */}
            <div className="flex-1 overflow-y-auto space-y-6 pt-4">
              {/* Search Inputs */}
              <div className="grid gap-4 sm:grid-cols-2">
                {/* Search Batter */}
                <div className="space-y-2 relative">
                  <label className="text-xs font-semibold text-textMuted uppercase tracking-wider">Search Batter</label>
                  <div className="relative">
                    <Search className="absolute left-3 top-3.5 h-4 w-4 text-textMuted" />
                    <input
                      type="text"
                      placeholder="e.g. MS Dhoni"
                      value={searchBatter}
                      onChange={(e) => setSearchBatter(e.target.value)}
                      className="w-full rounded-xl border border-slate-700 bg-slate-900 pl-10 pr-4 py-2.5 text-white placeholder-slate-500 outline-none focus:border-accentBlue"
                    />
                  </div>
                  {/* Results list */}
                  {batterResults.length > 0 && (
                    <div className="absolute z-10 w-full rounded-xl border border-slate-700 bg-slate-900 shadow-xl max-h-40 overflow-y-auto mt-1">
                      {batterResults.map(p => (
                        <button
                          key={p.name}
                          onClick={() => { setSelectedBatter(p.name); setSearchBatter(p.name); setBatterResults([]); }}
                          className="w-full text-left px-4 py-2 text-sm hover:bg-slate-800 text-white"
                        >
                          {p.name}
                        </button>
                      ))}
                    </div>
                  )}
                  {selectedBatter && (
                    <p className="text-xs text-accentBlue font-bold">Selected: {selectedBatter}</p>
                  )}
                </div>

                {/* Search Bowler */}
                <div className="space-y-2 relative">
                  <label className="text-xs font-semibold text-textMuted uppercase tracking-wider">Search Bowler</label>
                  <div className="relative">
                    <Search className="absolute left-3 top-3.5 h-4 w-4 text-textMuted" />
                    <input
                      type="text"
                      placeholder="e.g. SL Malinga"
                      value={searchBowler}
                      onChange={(e) => setSearchBowler(e.target.value)}
                      className="w-full rounded-xl border border-slate-700 bg-slate-900 pl-10 pr-4 py-2.5 text-white placeholder-slate-500 outline-none focus:border-accentGreen"
                    />
                  </div>
                  {/* Results list */}
                  {bowlerResults.length > 0 && (
                    <div className="absolute z-10 w-full rounded-xl border border-slate-700 bg-slate-900 shadow-xl max-h-40 overflow-y-auto mt-1">
                      {bowlerResults.map(p => (
                        <button
                          key={p.name}
                          onClick={() => { setSelectedBowler(p.name); setSearchBowler(p.name); setBowlerResults([]); }}
                          className="w-full text-left px-4 py-2 text-sm hover:bg-slate-800 text-white"
                        >
                          {p.name}
                        </button>
                      ))}
                    </div>
                  )}
                  {selectedBowler && (
                    <p className="text-xs text-accentGreen font-bold">Selected: {selectedBowler}</p>
                  )}
                </div>
              </div>

              {/* Action Button */}
              <button
                disabled={!selectedBatter || !selectedBowler || matchupLoading}
                onClick={getMatchup}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-accentBlue to-accentPurple font-extrabold text-white text-sm hover:opacity-95 disabled:opacity-40"
              >
                {matchupLoading ? 'Calculating...' : 'Launch Duel'}
              </button>

              {/* Matchup Duel Results Panel */}
              {matchupData && (
                <div className="rounded-2xl bg-slate-950 p-6 border border-slate-800 space-y-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="p-2 rounded-full bg-blue-500/10 text-accentBlue">
                        <User size={18} />
                      </div>
                      <div>
                        <h4 className="text-sm font-bold text-white">{selectedBatter}</h4>
                        <p className="text-[10px] text-textMuted">BATSMAN</p>
                      </div>
                    </div>
                    <span className="text-xs font-black text-textMuted uppercase italic">VS</span>
                    <div className="flex items-center gap-2 text-right">
                      <div>
                        <h4 className="text-sm font-bold text-white">{selectedBowler}</h4>
                        <p className="text-[10px] text-textMuted">BOWLER</p>
                      </div>
                      <div className="p-2 rounded-full bg-emerald-500/10 text-accentGreen">
                        <User size={18} />
                      </div>
                    </div>
                  </div>

                  {/* Metrics Table */}
                  {matchupData.runs === 0 && matchupData.balls === 0 ? (
                    <p className="text-center text-sm text-textMuted py-4">No head-to-head encounters recorded in IPL history.</p>
                  ) : (
                    <div className="grid grid-cols-3 gap-4 text-center">
                      <div className="p-3 bg-slate-900 rounded-xl">
                        <p className="text-xs text-textMuted">Runs Scored</p>
                        <p className="mt-1 text-lg font-extrabold text-white">{matchupData.runs}</p>
                      </div>
                      <div className="p-3 bg-slate-900 rounded-xl">
                        <p className="text-xs text-textMuted">Balls Faced</p>
                        <p className="mt-1 text-lg font-extrabold text-white">{matchupData.balls}</p>
                      </div>
                      <td className="p-3 bg-slate-900 rounded-xl">
                        <p className="text-xs text-textMuted">Dismissals</p>
                        <p className="mt-1 text-lg font-extrabold text-accentOrange">{matchupData.dismissals}</p>
                      </td>
                      <div className="p-3 bg-slate-900 rounded-xl">
                        <p className="text-xs text-textMuted">Strike Rate</p>
                        <p className="mt-1 text-lg font-extrabold text-accentBlue">{matchupData.strikeRate}</p>
                      </div>
                      <div className="p-3 bg-slate-900 rounded-xl">
                        <p className="text-xs text-textMuted">Fours / Sixes</p>
                        <p className="mt-1 text-lg font-extrabold text-white">{matchupData.fours} / {matchupData.sixes}</p>
                      </div>
                      <div className="p-3 bg-slate-900 rounded-xl">
                        <p className="text-xs text-textMuted">Dot Balls</p>
                        <p className="mt-1 text-lg font-extrabold text-textMuted">{matchupData.dots}</p>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
