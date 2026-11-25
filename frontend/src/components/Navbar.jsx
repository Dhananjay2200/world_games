import React from 'react';
import {
  Trophy,
  Flame,
  Shield,
  Clock,
  Sparkles,
  Globe2,
  Calendar,
  Layers,
  Award,
} from 'lucide-react';

export default function Navbar({ currentView, setCurrentView, stats, nextTimerSeconds }) {
  const formatTimer = (seconds) => {
    if (seconds == null || seconds < 0) return "--:--";
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-slate-950/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo & Tagline */}
        <div 
          onClick={() => setCurrentView('user')} 
          className="flex items-center gap-3 cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 p-0.5 shadow-lg shadow-emerald-500/20 group-hover:scale-105 transition-transform">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Trophy className="w-5 h-5 text-emerald-400 group-hover:rotate-6 transition-transform" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-extrabold text-lg text-white tracking-tight">WorldGames</span>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-black uppercase tracking-wider bg-emerald-500 text-slate-950">
                AI
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">Global Sports & Games Encyclopedia</p>
          </div>
        </div>

        {/* Live Sports Ticker Badges (Desktop) */}
        <div className="hidden lg:flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs">
            <Trophy className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-slate-400">Total Games:</span>
            <span className="font-bold text-white">{stats?.total_articles ?? 0}</span>
          </div>

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs">
            <Flame className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-slate-400">Daily Published:</span>
            <span className="font-bold text-emerald-400">{stats?.daily_published ?? 0} / {stats?.daily_limit ?? 200}</span>
          </div>

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs">
            <Clock className="w-3.5 h-3.5 text-sky-400" />
            <span className="text-slate-400">Next Game Guide:</span>
            <span className="font-mono font-bold text-sky-400">{formatTimer(nextTimerSeconds)}</span>
          </div>

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs">
            <Award className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-slate-400">Avg Quality:</span>
            <span className="font-bold text-amber-400">{stats?.average_score?.toFixed(1) ?? '9.0'}/10</span>
          </div>
        </div>

        {/* View Switcher / Admin Button */}
        <div className="flex items-center gap-3">
          {currentView === 'user' ? (
            <button
              onClick={() => setCurrentView('admin')}
              className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700/80 transition-all hover:border-emerald-500/50"
            >
              <Shield className="w-4 h-4 text-emerald-400" />
              <span>Admin Arena</span>
            </button>
          ) : (
            <button
              onClick={() => setCurrentView('user')}
              className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-emerald-500 hover:bg-emerald-400 text-slate-950 transition-all shadow-md shadow-emerald-500/20"
            >
              <Globe2 className="w-4 h-4" />
              <span>Visitor Arena</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
