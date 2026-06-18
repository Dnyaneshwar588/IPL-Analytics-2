import React, { useEffect, useState } from 'react';
import { MapPin, Shield, Zap } from 'lucide-react';

export default function Venues() {
  const [venues, setVenues] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchVenues() {
      try {
        const res = await fetch('/api/venues');
        const data = await res.json();
        setVenues(data);
      } catch (err) {
        console.error('Error fetching venues:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchVenues();
  }, []);

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-accentBlue border-t-transparent"></div>
      </div>
    );
  }

  // Get color code based on average score
  function getScoreColorClass(score) {
    if (score >= 170) return 'text-accentOrange';
    if (score >= 155) return 'text-accentYellow';
    return 'text-accentBlue';
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-white md:text-4xl">Stadium & Venue Insights</h1>
        <p className="mt-2 text-textMuted">Explore stadium profiles, run averages, and win patterns across IPL grounds.</p>
        <div className="mt-4 h-1 w-20 rounded bg-gradient-to-r from-accentBlue to-accentPurple"></div>
      </div>

      {/* Grid of Venue Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {venues.map((v) => {
          const chaseWinPct = (100 - v.batFirstWinPct).toFixed(2);
          
          return (
            <div key={v.venue} className="glass-card p-6 space-y-6 flex flex-col justify-between">
              {/* Venue Info */}
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <div className="p-3 bg-blue-500/10 text-accentBlue rounded-xl">
                    <MapPin size={20} />
                  </div>
                  <span className="text-[10px] font-bold tracking-wider uppercase bg-slate-800 text-textMuted px-2.5 py-1 rounded-full border border-slate-700/50">
                    {v.matchesPlayed} Matches
                  </span>
                </div>
                <h3 className="text-base font-extrabold text-white line-clamp-1" title={v.venue}>
                  {v.venue}
                </h3>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-2 gap-4 py-4 border-t border-b border-slate-800/40">
                <div>
                  <p className="text-[10px] uppercase font-bold tracking-wider text-textMuted">Avg 1st Inn Score</p>
                  <p className={`mt-1 text-2xl font-black ${getScoreColorClass(v.avgFirstInningsScore)}`}>
                    {v.avgFirstInningsScore}
                  </p>
                </div>
                <div>
                  <p className="text-[10px] uppercase font-bold tracking-wider text-textMuted">Bat First Win Rate</p>
                  <p className="mt-1 text-2xl font-black text-white">
                    {v.batFirstWinPct}%
                  </p>
                </div>
              </div>

              {/* Win percentage visual progress bar */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs font-semibold">
                  <span className="text-accentBlue">Bat First ({v.batFirstWinPct}%)</span>
                  <span className="text-accentOrange">Chasing ({chaseWinPct}%)</span>
                </div>
                <div className="w-full bg-slate-900 rounded-full h-2.5 overflow-hidden flex border border-slate-800">
                  <div 
                    className="bg-gradient-to-r from-accentBlue to-blue-500 h-full" 
                    style={{ width: `${v.batFirstWinPct}%` }}
                  ></div>
                  <div 
                    className="bg-gradient-to-r from-orange-500 to-accentOrange h-full" 
                    style={{ width: `${chaseWinPct}%` }}
                  ></div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
