import React, { useEffect, useState } from 'react';
import { Search, Flame, Shield, X, User, ChevronUp, ChevronDown } from 'lucide-react';
import { useToastContext } from '../context/ToastContext';

export default function Players() {
  const toast = useToastContext();
  const [topBatsmen, setTopBatsmen] = useState([]);
  const [topBowlers, setTopBowlers] = useState([]);
  const [loading, setLoading] = useState(true);

  // Sorting state
  const [batSortKey, setBatSortKey] = useState('runs');
  const [batSortOrder, setBatSortOrder] = useState('desc');
  const [bowlSortKey, setBowlSortKey] = useState('wickets');
  const [bowlSortOrder, setBowlSortOrder] = useState('desc');

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
      toast.success(`Duel data loaded: ${selectedBatter} vs ${selectedBowler}`);
    } catch (err) {
      console.error(err);
      toast.error('Failed to load matchup data');
    } finally {
      setMatchupLoading(false);
    }
  }

  // Sorting helpers
  const handleBatSortToggle = (key) => {
    if (batSortKey === key) {
      setBatSortOrder(batSortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setBatSortKey(key);
      setBatSortOrder('desc');
    }
  };

  const handleBowlSortToggle = (key) => {
    if (bowlSortKey === key) {
      setBowlSortOrder(bowlSortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setBowlSortKey(key);
      setBowlSortOrder('desc');
    }
  };

  const sortData = (data, key, order) => {
    return [...data].sort((a, b) => {
      let aVal, bVal;
      
      if (key === 'name') {
        aVal = a.name;
        bVal = b.name;
      } else if (key === 'runs') {
        aVal = a.battingStats.runs;
        bVal = b.battingStats.runs;
      } else if (key === 'average') {
        aVal = parseFloat(a.battingStats.average) || 0;
        bVal = parseFloat(b.battingStats.average) || 0;
      } else if (key === 'strikeRate') {
        aVal = parseFloat(a.battingStats.strikeRate) || 0;
        bVal = parseFloat(b.battingStats.strikeRate) || 0;
      } else if (key === 'wickets') {
        aVal = a.bowlingStats.wickets;
        bVal = b.bowlingStats.wickets;
      } else if (key === 'economy') {
        aVal = parseFloat(a.bowlingStats.economy) || 0;
        bVal = parseFloat(b.bowlingStats.economy) || 0;
      }
      
      if (typeof aVal === 'string') {
        return order === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      }
      return order === 'asc' ? aVal - bVal : bVal - aVal;
    });
  };

  const SortableHeader = ({ children, sortKey, currentSort, currentOrder, onSort }) => (
    <th 
      className="py-3 px-4 text-center cursor-pointer hover:bg-slate-800/30 transition-colors"
      onClick={() => onSort(sortKey)}
    >
      <div className="flex items-center justify-center gap-1">
        {children}
        {currentSort === sortKey && (
          currentOrder === 'asc' ? <ChevronUp size={14} /> : <ChevronDown size={14} />
        )}
      </div>
    </th>
  );

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
            <h3 className="text-lg font-bold text-white">Top Batsmen</h3>
            <span className="text-xs bg-accentBlue/20 text-accentBlue px-2 py-1 rounded-full font-semibold">{topBatsmen.length}</span>
          </div>
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th className="py-3 px-4 text-left">Player</th>
                  <SortableHeader 
                    sortKey="runs" 
                    currentSort={batSortKey} 
                    currentOrder={batSortOrder} 
                    onSort={handleBatSortToggle}
                  >
                    Runs
                  </SortableHeader>
                  <SortableHeader 
                    sortKey="average" 
                    currentSort={batSortKey} 
                    currentOrder={batSortOrder} 
                    onSort={handleBatSortToggle}
                  >
                    Avg
                  </SortableHeader>
                  <SortableHeader 
                    sortKey="strikeRate" 
                    currentSort={batSortKey} 
                    currentOrder={batSortOrder} 
                    onSort={handleBatSortToggle}
                  >
                    SR
                  </SortableHeader>
                </tr>
              </thead>
              <tbody>
                {sortData(topBatsmen, batSortKey, batSortOrder).map((player, idx) => (
                  <tr key={player.name}>
                    <td className="py-3 px-4 font-semibold text-white">
                      <div className="flex items-center gap-3">
                        <div className="flex h-6 w-6 items-center justify-center rounded-full bg-accentBlue/20 text-accentBlue text-xs font-bold">
                          {idx + 1}
                        </div>
                        <span className="line-clamp-1">{player.name}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-center font-bold text-gradient-text">{player.battingStats.runs}</td>
                    <td className="py-3 px-4 text-center text-textMain">{player.battingStats.average}</td>
                    <td className="py-3 px-4 text-center text-accentBlue font-semibold">{player.battingStats.strikeRate}</td>
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
            <h3 className="text-lg font-bold text-white">Top Bowlers</h3>
            <span className="text-xs bg-accentGreen/20 text-accentGreen px-2 py-1 rounded-full font-semibold">{topBowlers.length}</span>
          </div>
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th className="py-3 px-4 text-left">Player</th>
                  <SortableHeader 
                    sortKey="wickets" 
                    currentSort={bowlSortKey} 
                    currentOrder={bowlSortOrder} 
                    onSort={handleBowlSortToggle}
                  >
                    Wickets
                  </SortableHeader>
                  <SortableHeader 
                    sortKey="economy" 
                    currentSort={bowlSortKey} 
                    currentOrder={bowlSortOrder} 
                    onSort={handleBowlSortToggle}
                  >
                    Econ
                  </SortableHeader>
                  <SortableHeader 
                    sortKey="average" 
                    currentSort={bowlSortKey} 
                    currentOrder={bowlSortOrder} 
                    onSort={handleBowlSortToggle}
                  >
                    Avg
                  </SortableHeader>
                </tr>
              </thead>
              <tbody>
                {sortData(topBowlers, bowlSortKey, bowlSortOrder).map((player, idx) => (
                  <tr key={player.name}>
                    <td className="py-3 px-4 font-semibold text-white">
                      <div className="flex items-center gap-3">
                        <div className="flex h-6 w-6 items-center justify-center rounded-full bg-accentGreen/20 text-accentGreen text-xs font-bold">
                          {idx + 1}
                        </div>
                        <span className="line-clamp-1">{player.name}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-center font-bold text-gradient-green-text">{player.bowlingStats.wickets}</td>
                    <td className="py-3 px-4 text-center text-textMain">{player.bowlingStats.economy}</td>
                    <td className="py-3 px-4 text-center text-accentGreen font-semibold">{player.bowlingStats.average}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
          <div className="glass-card w-full max-w-2xl overflow-hidden relative p-6 max-h-[90vh] flex flex-col animate-slide-down">
            {/* Modal Header */}
            <div className="flex items-center justify-between pb-4 border-b border-slate-700">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Flame size={20} className="text-accentBlue" /> Head-to-Head Duel Creator
              </h3>
              <button 
                onClick={() => { setShowModal(false); setMatchupData(null); }} 
                className="text-slate-400 hover:text-white transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Body */}
            <div className="flex-1 overflow-y-auto space-y-6 pt-4 scrollbar-thin">
              {/* Search Inputs */}
              <div className="grid gap-4 sm:grid-cols-2">
                {/* Search Batter */}
                <div className="space-y-2.5 relative">
                  <label className="form-label">Search Batter</label>
                  <div className="relative">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-slate-500 pointer-events-none" />
                    <input
                      type="text"
                      placeholder="e.g. MS Dhoni"
                      value={searchBatter}
                      onChange={(e) => setSearchBatter(e.target.value)}
                      className="form-input pl-10"
                      autoComplete="off"
                    />
                  </div>
                  {/* Results list */}
                  {batterResults.length > 0 && (
                    <div className="absolute z-10 w-full rounded-xl border border-slate-700 bg-slate-900 shadow-xl max-h-40 overflow-y-auto mt-1">
                      {batterResults.map(p => (
                        <button
                          key={p.name}
                          onClick={() => { setSelectedBatter(p.name); setSearchBatter(p.name); setBatterResults([]); }}
                          className="w-full text-left px-4 py-2.5 text-sm hover:bg-slate-800 text-white font-medium transition-colors border-b border-slate-800 last:border-b-0"
                        >
                          {p.name}
                        </button>
                      ))}
                    </div>
                  )}
                  {selectedBatter && (
                    <div className="badge badge-blue">
                      ✓ {selectedBatter}
                    </div>
                  )}
                </div>

                {/* Search Bowler */}
                <div className="space-y-2.5 relative">
                  <label className="form-label">Search Bowler</label>
                  <div className="relative">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-slate-500 pointer-events-none" />
                    <input
                      type="text"
                      placeholder="e.g. SL Malinga"
                      value={searchBowler}
                      onChange={(e) => setSearchBowler(e.target.value)}
                      className="form-input pl-10"
                      autoComplete="off"
                    />
                  </div>
                  {/* Results list */}
                  {bowlerResults.length > 0 && (
                    <div className="absolute z-10 w-full rounded-xl border border-slate-700 bg-slate-900 shadow-xl max-h-40 overflow-y-auto mt-1">
                      {bowlerResults.map(p => (
                        <button
                          key={p.name}
                          onClick={() => { setSelectedBowler(p.name); setSearchBowler(p.name); setBowlerResults([]); }}
                          className="w-full text-left px-4 py-2.5 text-sm hover:bg-slate-800 text-white font-medium transition-colors border-b border-slate-800 last:border-b-0"
                        >
                          {p.name}
                        </button>
                      ))}
                    </div>
                  )}
                  {selectedBowler && (
                    <div className="badge badge-green">
                      ✓ {selectedBowler}
                    </div>
                  )}
                </div>
              </div>

              {/* Action Button */}
              <button
                disabled={!selectedBatter || !selectedBowler || matchupLoading}
                onClick={getMatchup}
                className="btn btn-primary w-full justify-center"
              >
                {matchupLoading ? 'Calculating...' : 'Launch Duel'}
              </button>

              {/* Matchup Duel Results Panel */}
              {matchupData && (
                <div className="rounded-xl bg-gradient-to-br from-slate-900 to-slate-800/50 p-6 border border-slate-700 space-y-6 animate-fade-in">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="p-2 rounded-full bg-accentBlue/20 text-accentBlue">
                        <User size={18} />
                      </div>
                      <div>
                        <h4 className="text-sm font-bold text-white">{selectedBatter}</h4>
                        <p className="text-[10px] text-textMuted uppercase font-semibold">Batsman</p>
                      </div>
                    </div>
                    <span className="text-xs font-black text-textMuted uppercase italic">VS</span>
                    <div className="flex items-center gap-2 text-right">
                      <div>
                        <h4 className="text-sm font-bold text-white">{selectedBowler}</h4>
                        <p className="text-[10px] text-textMuted uppercase font-semibold">Bowler</p>
                      </div>
                      <div className="p-2 rounded-full bg-accentGreen/20 text-accentGreen">
                        <User size={18} />
                      </div>
                    </div>
                  </div>

                  {/* Metrics Table */}
                  {matchupData.runs === 0 && matchupData.balls === 0 ? (
                    <div className="alert alert-info text-center py-4">
                      No head-to-head encounters recorded in IPL history.
                    </div>
                  ) : (
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-center">
                      <div className="p-4 bg-slate-900/80 rounded-lg border border-slate-700/50">
                        <p className="text-xs text-textMuted font-semibold">Runs Scored</p>
                        <p className="mt-2 text-2xl font-extrabold gradient-text">{matchupData.runs}</p>
                      </div>
                      <div className="p-4 bg-slate-900/80 rounded-lg border border-slate-700/50">
                        <p className="text-xs text-textMuted font-semibold">Balls Faced</p>
                        <p className="mt-2 text-2xl font-extrabold text-white">{matchupData.balls}</p>
                      </div>
                      <div className="p-4 bg-slate-900/80 rounded-lg border border-slate-700/50">
                        <p className="text-xs text-textMuted font-semibold">Dismissals</p>
                        <p className="mt-2 text-2xl font-extrabold text-accentOrange">{matchupData.dismissals}</p>
                      </div>
                      <div className="p-4 bg-slate-900/80 rounded-lg border border-slate-700/50">
                        <p className="text-xs text-textMuted font-semibold">Strike Rate</p>
                        <p className="mt-2 text-2xl font-extrabold text-accentBlue">{matchupData.strikeRate}</p>
                      </div>
                      <div className="p-4 bg-slate-900/80 rounded-lg border border-slate-700/50">
                        <p className="text-xs text-textMuted font-semibold">Fours / Sixes</p>
                        <p className="mt-2 text-2xl font-extrabold text-white">{matchupData.fours} / {matchupData.sixes}</p>
                      </div>
                      <div className="p-4 bg-slate-900/80 rounded-lg border border-slate-700/50">
                        <p className="text-xs text-textMuted font-semibold">Dot Balls</p>
                        <p className="mt-2 text-2xl font-extrabold text-slate-400">{matchupData.dots}</p>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
    </div>
  );
}
