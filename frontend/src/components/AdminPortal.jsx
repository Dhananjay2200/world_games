import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Shield,
  Trophy,
  Flame,
  Clock,
  Play,
  Square,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  Trash2,
  Eye,
  Send,
  Sparkles,
  Layers,
  Filter,
  Award,
  Globe2,
  Calendar,
  Lock,
  BookOpen,
  Radio,
  Zap,
} from 'lucide-react';
import { CATEGORY_CONFIG, REGIONS, getCategoryConfig } from '../utils/sportsIcons';
import PlaybookModal from './PlaybookModal';
import { apiUrl } from '../config';

export default function AdminPortal({ stats, onRefreshStats }) {
  // Authentication State
  const [token, setToken] = useState(() => localStorage.getItem('worldgames_admin_token') || '');
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [authError, setAuthError] = useState('');

  // Articles & Management State
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedIds, setSelectedIds] = useState([]);
  const [activeTab, setActiveTab] = useState('ALL'); // ALL, IN_REVIEW, PUBLISHED
  const [actionMessage, setActionMessage] = useState('');

  // Immediate Generation Modal
  const [showGenModal, setShowGenModal] = useState(false);
  const [genArticleType, setGenArticleType] = useState('NEWS'); // 'PLAYBOOK' or 'NEWS'
  const [genTopicName, setGenTopicName] = useState('Kabaddi');
  const [genNewsAngle, setGenNewsAngle] = useState('Pro Kabaddi League 2026: Finals MVP & Tactical Review');
  const [genRegion, setGenRegion] = useState('South Asia');
  const [genCategory, setGenCategory] = useState('Indigenous, Folk & Traditional Games');
  const [isGenerating, setIsGenerating] = useState(false);

  // Live 1-second clock tick for Next Post & 1-Day Reset countdown timers
  const [nowMs, setNowMs] = useState(() => Date.now());

  useEffect(() => {
    const tick = setInterval(() => setNowMs(Date.now()), 1000);
    return () => clearInterval(tick);
  }, []);

  const parseUtcIso = (isoStr) => {
    if (!isoStr) return null;
    const hasZone = /([zZ]|[+-]\d{2}:\d{2})$/.test(isoStr);
    const parsed = new Date(hasZone ? isoStr : `${isoStr}Z`);
    return Number.isNaN(parsed.getTime()) ? null : parsed.getTime();
  };

  const formatDuration = (totalSeconds, alwaysHours = false) => {
    const secs = Math.max(0, Math.floor(totalSeconds));
    const hrs = Math.floor(secs / 3600);
    const mins = Math.floor((secs % 3600) / 60);
    const rem = secs % 60;
    if (alwaysHours || hrs > 0) {
      return `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(rem).padStart(2, '0')}`;
    }
    return `${String(mins).padStart(2, '0')}:${String(rem).padStart(2, '0')}`;
  };

  const getNextPostTimer = () => {
    if (!stats?.is_automation_running) {
      return { value: 'Paused', sub: 'Start daemon to schedule', active: false };
    }
    const nextRunMs = parseUtcIso(stats?.next_run_at);
    if (!nextRunMs) {
      return { value: '05:00', sub: 'Scheduled cycle queued', active: true };
    }
    const diffSecs = Math.floor((nextRunMs - nowMs) / 1000);
    if (diffSecs <= 0) {
      return { value: 'Running...', sub: 'Publishing cycle in progress', active: true };
    }
    return {
      value: formatDuration(diffSecs, false),
      sub: `Next post at ${new Date(nextRunMs).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`,
      active: true,
    };
  };

  const getDailyResetTimer = () => {
    const current = new Date(nowMs);
    const nextMidnight = new Date(
      current.getFullYear(),
      current.getMonth(),
      current.getDate() + 1,
      0,
      0,
      0
    );
    const diffSecs = Math.max(0, Math.floor((nextMidnight.getTime() - nowMs) / 1000));
    return {
      value: formatDuration(diffSecs, true),
      sub: 'Resets daily quota (00:00)',
    };
  };

  const nextPostTimer = getNextPostTimer();
  const dailyResetTimer = getDailyResetTimer();

  // Active Preview Modal
  const [previewArticle, setPreviewArticle] = useState(null);

  // Login handler
  const handleLogin = async (e) => {
    e.preventDefault();
    setAuthError('');
    const cleanUser = (username || '').trim();
    const cleanPass = (password || '').trim();

    if (!cleanUser || !cleanPass) {
      setAuthError('Please enter both username and password.');
      return;
    }

    try {
      const res = await fetch(apiUrl('/api/v1/auth/login'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: cleanUser, password: cleanPass }),
      });

      if (res.ok) {
        const data = await res.json();
        const authToken = data.access_token || data.token;
        if (authToken) {
          setToken(authToken);
          localStorage.setItem('worldgames_admin_token', authToken);
          setAuthError('');
        } else {
          setAuthError('Authentication succeeded but session token was missing.');
        }
      } else {
        const errorData = await res.json().catch(() => ({}));
        setAuthError(errorData.detail || `Login rejected by server (Status ${res.status}). Verify credentials.`);
      }
    } catch (err) {
      setAuthError(`Connection error: ${err.message}. Please verify the WorldGames backend is running on port 8001.`);
    }
  };

  const handleLogout = () => {
    setToken('');
    localStorage.removeItem('worldgames_admin_token');
  };

  const notifyPublicTabs = () => {
    if (typeof BroadcastChannel !== 'undefined') {
      const ch = new BroadcastChannel('worldgames_updates');
      ch.postMessage({ type: 'ARTICLES_UPDATED' });
      ch.close();
    }
  };

  // Fetch articles for management (supports silent live updates without table flicker)
  const fetchAdminArticles = useCallback(async ({ silent = false } = {}) => {
    if (!silent) {
      setLoading(true);
    }
    try {
      let url = apiUrl('/api/v1/articles?limit=100');
      if (activeTab === 'IN_REVIEW') {
        url = apiUrl('/api/v1/publish/review-queue?limit=100');
      }

      const res = await fetch(url, { cache: 'no-store' });
      if (res.ok) {
        const data = await res.json();
        let list = data.articles || [];
        if (activeTab === 'PUBLISHED') {
          list = list.filter((a) => a.status === 'PUBLISHED');
        }
        setArticles(list);
      }
    } catch (e) {
      console.error('Failed to load admin articles:', e);
    } finally {
      if (!silent) {
        setLoading(false);
      }
    }
  }, [activeTab]);

  useEffect(() => {
    if (token) {
      fetchAdminArticles({ silent: false });
    }
  }, [token, fetchAdminArticles]);

  // Automatically refresh table whenever live backend stats change (e.g. daemon auto-publishes a story)
  const lastAdminStatsSig = useRef(null);

  useEffect(() => {
    if (!token || !stats) return;
    const sig = `${stats.total_articles ?? 0}:${stats.total_playbooks ?? 0}:${stats.total_news ?? 0}:${stats.in_review_count ?? 0}`;
    if (lastAdminStatsSig.current === null) {
      lastAdminStatsSig.current = sig;
      return;
    }
    if (lastAdminStatsSig.current !== sig) {
      lastAdminStatsSig.current = sig;
      fetchAdminArticles({ silent: true });
    }
  }, [token, stats, fetchAdminArticles]);

  // Background fallback sync every 10s & on tab focus
  useEffect(() => {
    if (!token) return;
    const bgSync = setInterval(() => {
      fetchAdminArticles({ silent: true });
    }, 10000);
    const onFocus = () => {
      if (document.visibilityState === 'visible') {
        fetchAdminArticles({ silent: true });
        if (onRefreshStats) onRefreshStats();
      }
    };
    document.addEventListener('visibilitychange', onFocus);
    return () => {
      clearInterval(bgSync);
      document.removeEventListener('visibilitychange', onFocus);
    };
  }, [token, fetchAdminArticles, onRefreshStats]);

  // Selection handlers
  const handleSelectAll = (e) => {
    if (e.target.checked) {
      setSelectedIds(articles.map((a) => a.id));
    } else {
      setSelectedIds([]);
    }
  };

  const handleToggleSelect = (id) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  // Batch Publish Selected
  const handleBatchPublish = async () => {
    if (selectedIds.length === 0) return;
    try {
      const res = await fetch(apiUrl('/api/v1/publish/batch'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ article_ids: selectedIds }),
      });
      if (res.ok) {
        const data = await res.json();
        setActionMessage(data.message || 'Articles published successfully!');
        setSelectedIds([]);
        await fetchAdminArticles({ silent: true });
        if (onRefreshStats) await onRefreshStats();
        notifyPublicTabs();
      }
    } catch (e) {
      console.error(e);
    }
  };

  // Single Publish
  const handleSinglePublish = async (id) => {
    try {
      const res = await fetch(apiUrl(`/api/v1/publish/${id}`), {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setActionMessage(`Article ${id} published successfully.`);
        await fetchAdminArticles({ silent: true });
        if (onRefreshStats) await onRefreshStats();
        notifyPublicTabs();
      }
    } catch (e) {
      console.error(e);
    }
  };

  // Delete / Reject Article
  const handleDeleteArticle = async (id) => {
    if (!window.confirm(`Are you sure you want to delete article ${id}?`)) return;
    try {
      const res = await fetch(apiUrl(`/api/v1/publish/${id}`), {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setActionMessage(`Article ${id} deleted.`);
        await fetchAdminArticles({ silent: true });
        if (onRefreshStats) await onRefreshStats();
        notifyPublicTabs();
      }
    } catch (e) {
      console.error(e);
    }
  };

  // Trigger Immediate LangGraph Generation
  const handleRunGeneration = async (e) => {
    e.preventDefault();
    setIsGenerating(true);
    setActionMessage('');
    try {
      const payload = {
        name: genTopicName.trim() || undefined,
        region: genRegion,
        category: genCategory,
        article_type: genArticleType,
        news_angle: genArticleType === 'NEWS' ? genNewsAngle : undefined,
      };

      const res = await fetch(apiUrl('/api/v1/workflow/run'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data = await res.json();
        setActionMessage(`[+] Generated: "${data.workflow_result?.article_title || 'Game Story'}" [Type: ${data.workflow_result?.article_type}, Score: ${data.workflow_result?.score}/10]`);
        setShowGenModal(false);
        await fetchAdminArticles({ silent: true });
        if (onRefreshStats) await onRefreshStats();
        notifyPublicTabs();
      }
    } catch (e) {
      setActionMessage('Workflow execution failed.');
    } finally {
      setIsGenerating(false);
    }
  };

  // Automation Toggle Loading State
  const [isTogglingAutomation, setIsTogglingAutomation] = useState(false);

  // Automation Daemon Toggle
  const toggleAutomation = async (start) => {
    setIsTogglingAutomation(true);
    try {
      const endpoint = apiUrl(start ? '/api/v1/automation/start' : '/api/v1/automation/stop');
      const body = start ? JSON.stringify({ interval_seconds: 300 }) : undefined;
      const res = await fetch(endpoint, {
        method: 'POST',
        cache: 'no-store',
        headers: { 'Content-Type': 'application/json' },
        body,
      });
      if (res.ok) {
        const data = await res.json().catch(() => ({}));
        setActionMessage(
          data.message || (start ? 'Autonomous daemon started.' : 'Autonomous daemon paused.')
        );
        if (onRefreshStats) {
          await onRefreshStats();
        }
      } else {
        setActionMessage(`Failed to ${start ? 'start' : 'pause'} daemon (Status ${res.status}).`);
      }
    } catch (e) {
      console.error(e);
      setActionMessage(`Connection error while trying to ${start ? 'start' : 'pause'} daemon.`);
    } finally {
      setIsTogglingAutomation(false);
    }
  };

  if (!token) {
    return (
      <div className="max-w-md mx-auto my-12 p-8 bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl glow-emerald">
        <div className="text-center space-y-2 mb-6">
          <div className="w-12 h-12 bg-emerald-500/10 text-emerald-400 rounded-2xl flex items-center justify-center mx-auto border border-emerald-500/30">
            <Lock className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-bold text-white">Admin Arena Gate</h2>
          <p className="text-xs text-slate-400">Authenticate to manage playbooks, sports news & batch publishing</p>
        </div>

        {authError && (
          <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-xs text-red-400 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{authError}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="text-xs font-semibold text-slate-400 block mb-1">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-2.5 bg-slate-950 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-400 block mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2.5 bg-slate-950 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:border-emerald-500"
            />
          </div>

          <button
            type="submit"
            className="w-full py-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm transition-all shadow-lg shadow-emerald-500/20"
          >
            Enter Admin Arena
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-16">
      {/* Admin Arena Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-white flex items-center gap-2.5">
            <Shield className="w-7 h-7 text-emerald-400" />
            WorldGames Admin Command
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Autonomous Engine Monitor, Sports News Dispatcher & Playbook Manager
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowGenModal(true)}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-emerald-500 to-teal-400 text-slate-950 hover:brightness-110 shadow-lg shadow-emerald-500/20"
          >
            <Sparkles className="w-4 h-4" />
            Generate Playbook or News
          </button>

          <button
            onClick={handleLogout}
            className="px-3 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
          >
            Logout
          </button>
        </div>
      </div>

      {actionMessage && (
        <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-xs text-emerald-300 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{actionMessage}</span>
          </div>
          <button onClick={() => setActionMessage('')} className="text-slate-400 hover:text-white text-xs">
            Dismiss
          </button>
        </div>
      )}

      {/* Scoreboard Statistics Bar */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Playbooks</span>
            <BookOpen className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-white">{stats?.total_playbooks ?? stats?.total_articles ?? 0}</div>
          <div className="text-[11px] text-emerald-400 font-medium">Foundational Guides</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Sports News</span>
            <Radio className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-black text-amber-400">{stats?.total_news ?? 0}</div>
          <div className="text-[11px] text-slate-400">Tournaments & Updates</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Daily Published</span>
            <Flame className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-emerald-400">
            {stats?.daily_published ?? 0} <span className="text-sm font-normal text-slate-500">/ {stats?.daily_limit ?? 200}</span>
          </div>
          <div className="text-[11px] text-slate-400">Resets in <span className="font-mono text-emerald-400">{dailyResetTimer.value}</span></div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Under Review</span>
            <AlertCircle className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl font-black text-rose-400">{stats?.in_review_count ?? 0}</div>
          <div className="text-[11px] text-slate-400">Awaiting Decision</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Average Score</span>
            <Award className="w-4 h-4 text-sky-400" />
          </div>
          <div className="text-2xl font-black text-sky-400">{stats?.average_score?.toFixed(1) ?? '9.0'}/10</div>
          <div className="text-[11px] text-slate-400">Quality Gate Rating</div>
        </div>
      </div>

      {/* Live Timers & Autonomous Continuous Engine Controller */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 flex items-center justify-between">
          <div className="space-y-1">
            <div className="text-xs text-slate-400 flex items-center gap-1.5 font-medium">
              <Clock className="w-4 h-4 text-sky-400" />
              <span>Next Post Timer</span>
            </div>
            <div className={`text-2xl font-black font-mono ${nextPostTimer.active ? 'text-sky-400' : 'text-slate-400'}`}>
              {nextPostTimer.value}
            </div>
            <div className="text-[11px] text-slate-400">{nextPostTimer.sub}</div>
          </div>
          <span className={`px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider border ${
            nextPostTimer.active
              ? 'bg-sky-500/15 text-sky-400 border-sky-500/30'
              : 'bg-slate-800 text-slate-400 border-slate-700'
          }`}>
            {nextPostTimer.active ? 'Auto Cycle' : 'Idle'}
          </span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 flex items-center justify-between">
          <div className="space-y-1">
            <div className="text-xs text-slate-400 flex items-center gap-1.5 font-medium">
              <Calendar className="w-4 h-4 text-amber-400" />
              <span>Next 1-Day Reset Timer</span>
            </div>
            <div className="text-2xl font-black font-mono text-amber-400">
              {dailyResetTimer.value}
            </div>
            <div className="text-[11px] text-slate-400">{dailyResetTimer.sub}</div>
          </div>
          <span className="px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider bg-amber-500/15 text-amber-400 border border-amber-500/30">
            24h Window
          </span>
        </div>
      </div>

      {/* Autonomous Continuous Engine Controller */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${stats?.is_automation_running ? 'bg-emerald-500 animate-ping' : 'bg-slate-600'}`} />
          <div>
            <div className="text-sm font-bold text-white flex items-center gap-2">
              <span>Autonomous Generator Daemon (Target: 200/Day)</span>
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                stats?.is_automation_running ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-slate-800 text-slate-400'
              }`}>
                {stats?.is_automation_running ? 'RUNNING' : 'STOPPED'}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Continuously balances discovery across 10 regions & 12 categories, writing and auto-publishing.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {stats?.is_automation_running ? (
            <button
              onClick={() => toggleAutomation(false)}
              disabled={isTogglingAutomation}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40 hover:bg-rose-500/30 disabled:opacity-50 transition-colors"
            >
              <Square className="w-3.5 h-3.5 fill-current" />
              {isTogglingAutomation ? 'Pausing...' : 'Pause Daemon'}
            </button>
          ) : (
            <button
              onClick={() => toggleAutomation(true)}
              disabled={isTogglingAutomation}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold bg-emerald-500 text-slate-950 hover:bg-emerald-400 disabled:opacity-50 transition-colors shadow-md shadow-emerald-500/20"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              {isTogglingAutomation ? 'Starting...' : 'Start Daemon'}
            </button>
          )}
        </div>
      </div>

      {/* Article Manager Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden space-y-4 p-5">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div className="flex items-center gap-2">
            {[
              { id: 'ALL', label: 'All Stories' },
              { id: 'IN_REVIEW', label: `Under Review (${stats?.in_review_count ?? 0})` },
              { id: 'PUBLISHED', label: 'Published' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => { setActiveTab(tab.id); setSelectedIds([]); }}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                  activeTab === tab.id
                    ? 'bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/20'
                    : 'bg-slate-800/60 text-slate-400 hover:text-white'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-3">
            {selectedIds.length > 0 && (
              <button
                onClick={handleBatchPublish}
                className="flex items-center gap-1.5 px-4 py-1.5 rounded-xl text-xs font-bold bg-emerald-500 text-slate-950 hover:bg-emerald-400 transition-colors shadow-md shadow-emerald-500/25"
              >
                <CheckCircle2 className="w-4 h-4" />
                Batch Publish ({selectedIds.length})
              </button>
            )}

            <button
              onClick={() => fetchAdminArticles({ silent: false })}
              className="p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-white transition-colors"
              title="Refresh Table"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Playbook Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950/70 text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="p-3 w-10">
                  <input
                    type="checkbox"
                    onChange={handleSelectAll}
                    checked={articles.length > 0 && selectedIds.length === articles.length}
                    className="rounded border-slate-700 bg-slate-900 text-emerald-500 focus:ring-emerald-500"
                  />
                </th>
                <th className="p-3">Title / Story</th>
                <th className="p-3">Type</th>
                <th className="p-3">Category</th>
                <th className="p-3">Region & Origin</th>
                <th className="p-3">Score</th>
                <th className="p-3">Status</th>
                <th className="p-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading ? (
                <tr>
                  <td colSpan="8" className="p-8 text-center text-slate-400">
                    <RefreshCw className="w-5 h-5 text-emerald-400 animate-spin mx-auto mb-2" />
                    Loading stories...
                  </td>
                </tr>
              ) : articles.length === 0 ? (
                <tr>
                  <td colSpan="8" className="p-8 text-center text-slate-500">
                    No articles found in this view.
                  </td>
                </tr>
              ) : (
                articles.map((art) => {
                  const isSelected = selectedIds.includes(art.id);
                  const catConfig = getCategoryConfig(art.category);
                  const isNews = art.article_type === 'NEWS';

                  return (
                    <tr
                      key={art.id}
                      className={`hover:bg-slate-800/40 transition-colors ${
                        isSelected ? 'bg-emerald-500/5' : ''
                      }`}
                    >
                      <td className="p-3">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => handleToggleSelect(art.id)}
                          className="rounded border-slate-700 bg-slate-900 text-emerald-500 focus:ring-emerald-500"
                        />
                      </td>

                      <td className="p-3">
                        <div className="font-bold text-white hover:text-emerald-400 cursor-pointer" onClick={() => setPreviewArticle(art)}>
                          {art.title}
                        </div>
                        <div className="text-[11px] text-slate-500 mt-0.5">{art.slug}</div>
                      </td>

                      <td className="p-3">
                        {isNews ? (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-400 border border-amber-500/40">
                            <Zap className="w-3 h-3 fill-current" />
                            NEWS
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
                            <BookOpen className="w-3 h-3" />
                            PLAYBOOK
                          </span>
                        )}
                      </td>

                      <td className="p-3">
                        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold border ${catConfig.bg}`}>
                          {art.category}
                        </span>
                      </td>

                      <td className="p-3">
                        <div className="text-slate-300 font-medium">{art.origin_country}</div>
                        <div className="text-[11px] text-slate-500">{art.origin_region}</div>
                      </td>

                      <td className="p-3">
                        <span className="font-bold text-amber-400">{art.score?.toFixed(1)}/10</span>
                      </td>

                      <td className="p-3">
                        <span className={`inline-flex px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-wider ${
                          art.status === 'PUBLISHED'
                            ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                            : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                        }`}>
                          {art.status}
                        </span>
                      </td>

                      <td className="p-3 text-right space-x-1.5 whitespace-nowrap">
                        <button
                          onClick={() => setPreviewArticle(art)}
                          className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                          title="Preview"
                        >
                          <Eye className="w-3.5 h-3.5" />
                        </button>

                        {art.status !== 'PUBLISHED' && (
                          <button
                            onClick={() => handleSinglePublish(art.id)}
                            className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 transition-colors"
                            title="Publish"
                          >
                            <CheckCircle2 className="w-3.5 h-3.5" />
                          </button>
                        )}

                        <button
                          onClick={() => handleDeleteArticle(art.id)}
                          className="p-1.5 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors"
                          title="Delete"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Manual Game / News Generation Modal */}
      {showGenModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-6 space-y-5 glow-emerald">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="font-bold text-white text-base flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-emerald-400" />
                Launch LangGraph Story Generation
              </h3>
              <button onClick={() => setShowGenModal(false)} className="text-slate-400 hover:text-white">
                ✕
              </button>
            </div>

            <form onSubmit={handleRunGeneration} className="space-y-4 text-xs">
              {/* Type Selector */}
              <div>
                <label className="font-semibold text-slate-300 block mb-1">Story Type</label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setGenArticleType('NEWS')}
                    className={`py-2 px-3 rounded-xl border text-center font-bold flex items-center justify-center gap-1.5 ${
                      genArticleType === 'NEWS'
                        ? 'bg-amber-500/20 text-amber-400 border-amber-500'
                        : 'bg-slate-950 text-slate-400 border-slate-800'
                    }`}
                  >
                    <Radio className="w-3.5 h-3.5" />
                    Sports News
                  </button>

                  <button
                    type="button"
                    onClick={() => setGenArticleType('PLAYBOOK')}
                    className={`py-2 px-3 rounded-xl border text-center font-bold flex items-center justify-center gap-1.5 ${
                      genArticleType === 'PLAYBOOK'
                        ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500'
                        : 'bg-slate-950 text-slate-400 border-slate-800'
                    }`}
                  >
                    <BookOpen className="w-3.5 h-3.5" />
                    Playbook Guide
                  </button>
                </div>
              </div>

              <div>
                <label className="font-semibold text-slate-300 block mb-1">Sport / Game Name</label>
                <input
                  type="text"
                  value={genTopicName}
                  onChange={(e) => setGenTopicName(e.target.value)}
                  placeholder="e.g. Kabaddi, Hurling, Sepak Takraw, Curling..."
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500"
                />
              </div>

              {genArticleType === 'NEWS' && (
                <div>
                  <label className="font-semibold text-amber-400 block mb-1">News Headline / Angle</label>
                  <input
                    type="text"
                    value={genNewsAngle}
                    onChange={(e) => setGenNewsAngle(e.target.value)}
                    placeholder="e.g. Pro Kabaddi 2026: Finals MVP & Tactical Review"
                    className="w-full px-3 py-2 bg-slate-950 border border-amber-500/40 rounded-xl text-white focus:outline-none focus:border-amber-500"
                  />
                  <p className="text-[10px] text-slate-500 mt-1">This will be published as a fresh News article without touching any existing playbooks.</p>
                </div>
              )}

              <div>
                <label className="font-semibold text-slate-300 block mb-1">Target Region</label>
                <select
                  value={genRegion}
                  onChange={(e) => setGenRegion(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500"
                >
                  {REGIONS.filter(r => r !== 'All').map(r => (
                    <option key={r} value={r}>{r}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="font-semibold text-slate-300 block mb-1">Sports Category</label>
                <select
                  value={genCategory}
                  onChange={(e) => setGenCategory(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500"
                >
                  {Object.keys(CATEGORY_CONFIG).map(c => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              <div className="pt-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowGenModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isGenerating}
                  className="px-5 py-2 rounded-xl bg-emerald-500 text-slate-950 font-bold hover:bg-emerald-400 transition-colors flex items-center gap-1.5 shadow-md shadow-emerald-500/20"
                >
                  {isGenerating ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      Publishing News...
                    </>
                  ) : (
                    'Launch Pipeline'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Preview Playbook Modal */}
      {previewArticle && (
        <PlaybookModal
          article={previewArticle}
          onClose={() => setPreviewArticle(null)}
        />
      )}
    </div>
  );
}
