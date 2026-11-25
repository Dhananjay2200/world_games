import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import UserPortal from './components/UserPortal';
import AdminPortal from './components/AdminPortal';
import { Trophy, Globe2, Shield, Heart, Zap } from 'lucide-react';
import { apiUrl } from './config';

export default function App() {
  const [currentView, setCurrentView] = useState('user'); // 'user' or 'admin'
  const [stats, setStats] = useState(null);
  const [timerSeconds, setTimerSeconds] = useState(180); // countdown to next publish

  // Fetch real-time system stats
  const fetchStats = async () => {
    try {
      const res = await fetch(apiUrl('/api/v1/publish/stats'));
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (e) {
      console.error('Failed to fetch system stats:', e);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 15000);
    return () => clearInterval(interval);
  }, []);

  // Countdown timer effect
  useEffect(() => {
    const timer = setInterval(() => {
      setTimerSeconds((prev) => (prev > 0 ? prev - 1 : 180));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-emerald-500 selection:text-slate-950">
      {/* Sports Navigation Bar */}
      <Navbar
        currentView={currentView}
        setCurrentView={setCurrentView}
        stats={stats}
        nextTimerSeconds={timerSeconds}
      />

      {/* Main Content Arena */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-8">
        {currentView === 'user' ? (
          <UserPortal />
        ) : (
          <AdminPortal stats={stats} onRefreshStats={fetchStats} />
        )}
      </main>

      {/* Sports Arena Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950/80 backdrop-blur-md py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <Trophy className="w-4 h-4 text-emerald-500" />
            <span className="font-bold text-slate-300">WorldGames AI</span>
            <span>— Preserving and Celebrating the Athletic Heritage of Earth</span>
          </div>

          <div className="flex items-center gap-4">
            <span className="inline-flex items-center gap-1">
              <Zap className="w-3.5 h-3.5 text-amber-400" />
              LangGraph + NVIDIA NIM Autonomous Pipeline
            </span>
            <span className="text-slate-600">|</span>
            <span>Verified Wikimedia Commons Licensing</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
