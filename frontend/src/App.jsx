import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Trophy, Users, MapPin, Zap, Sparkles, Menu, X } from 'lucide-react';

// Pages
import Dashboard from './pages/Dashboard';
import Teams from './pages/Teams';
import Players from './pages/Players';
import Venues from './pages/Venues';
import Predictor from './pages/Predictor';
import FantasyXI from './pages/FantasyXI';

function Navigation() {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const menuItems = [
    { name: 'Dashboard', path: '/', icon: <LayoutDashboard size={18} /> },
    { name: 'Teams', path: '/teams', icon: <Trophy size={18} /> },
    { name: 'Players', path: '/players', icon: <Users size={18} /> },
    { name: 'Venues', path: '/venues', icon: <MapPin size={18} /> },
    { name: 'Match Predictor', path: '/predictor', icon: <Zap size={18} /> },
    { name: 'Fantasy XI', path: '/fantasy', icon: <Sparkles size={18} /> }
  ];

  return (
    <>
      {/* Mobile Header */}
      <header className="flex h-16 items-center justify-between border-b border-cardBorder bg-slate-950 px-6 lg:hidden">
        <div className="flex items-center gap-2">
          <span className="text-xl font-black tracking-tight text-white flex items-center gap-1.5">
            IPL <span className="text-accentBlue">PRO</span>
          </span>
        </div>
        <button onClick={() => setSidebarOpen(!sidebarOpen)} className="text-textMain">
          {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </header>

      {/* Sidebar Container */}
      <aside 
        className={`fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-cardBorder bg-slate-950 px-4 py-6 transition-transform duration-300 lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:static`}
      >
        {/* Logo */}
        <div className="mb-8 px-2 flex items-center gap-2">
          <span className="text-2xl font-black tracking-tight text-white">
            IPL <span className="text-accentBlue">PRO</span>
          </span>
          <span className="text-[10px] uppercase font-bold tracking-widest bg-accentBlue/10 text-accentBlue px-2 py-0.5 rounded border border-accentBlue/20">
            Console
          </span>
        </div>

        {/* Menu Items */}
        <nav className="flex-1 space-y-1">
          {menuItems.map((item) => {
            const isActive = location.pathname === item.path;
            
            return (
              <Link
                key={item.name}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={`flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-semibold transition-all duration-200 ${
                  isActive 
                    ? 'bg-slate-900 text-accentBlue shadow-inner' 
                    : 'text-textMuted hover:bg-slate-900/40 hover:text-textMain'
                }`}
              >
                {item.icon}
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* Footer info in sidebar */}
        <div className="border-t border-cardBorder pt-6 px-2 text-[10px] text-textMuted flex flex-col gap-1">
          <p>© 2026 IPL Analytics Pro</p>
          <p>Powered by XGBoost & LightGBM</p>
        </div>
      </aside>
    </>
  );
}

export default function App() {
  return (
    <Router>
      <div className="flex min-h-screen flex-col lg:flex-row bg-darkBg">
        {/* Navigation Sidebar */}
        <Navigation />

        {/* Main Content Area */}
        <main className="flex-1 px-6 py-8 md:px-8 overflow-y-auto max-h-screen">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/teams" element={<Teams />} />
            <Route path="/players" element={<Players />} />
            <Route path="/venues" element={<Venues />} />
            <Route path="/predictor" element={<Predictor />} />
            <Route path="/fantasy" element={<FantasyXI />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}
