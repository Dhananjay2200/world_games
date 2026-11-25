import React, { useState, useEffect } from 'react';
import {
  Search,
  Trophy,
  Filter,
  Calendar,
  Globe2,
  Clock,
  Award,
  ChevronRight,
  Flame,
  ArrowRight,
  Sparkles,
  MapPin,
  RefreshCw,
  X,
  Zap,
  BookOpen,
  Radio,
} from 'lucide-react';
import { CATEGORY_CONFIG, REGIONS, getCategoryConfig } from '../utils/sportsIcons';
import PlaybookModal from './PlaybookModal';

export default function UserPortal() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [totalCount, setTotalCount] = useState(0);

  // Combinatorial Filters
  const [storyType, setStoryType] = useState('All'); // 'All', 'PLAYBOOK', 'NEWS'
  const [selectedRegion, setSelectedRegion] = useState('All');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedDate, setSelectedDate] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  // Active Modal
  const [activeArticle, setActiveArticle] = useState(null);

  const fetchArticles = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (storyType !== 'All') params.append('article_type', storyType);
      if (selectedRegion !== 'All') params.append('region', selectedRegion);
      if (selectedCategory !== 'All') params.append('category', selectedCategory);
      if (selectedDate) params.append('date', selectedDate);
      if (searchQuery.trim()) params.append('search', searchQuery.trim());

      const res = await fetch(`/api/v1/publish/feed?${params.toString()}`);
      if (res.ok) {
        const data = await res.json();
        setArticles(data.articles || []);
        setTotalCount(data.total || 0);
      }
    } catch (e) {
      console.error('Error fetching game articles:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchArticles();
  }, [storyType, selectedRegion, selectedCategory, selectedDate]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchArticles();
  };

  const clearAllFilters = () => {
    setStoryType('All');
    setSelectedRegion('All');
    setSelectedCategory('All');
    setSelectedDate('');
    setSearchQuery('');
  };

  const activeFiltersCount = (storyType !== 'All' ? 1 : 0) +
    (selectedRegion !== 'All' ? 1 : 0) +
    (selectedCategory !== 'All' ? 1 : 0) +
    (selectedDate ? 1 : 0) +
    (searchQuery ? 1 : 0);

  return (
    <div className="space-y-8 pb-16">
      {/* Sports Stadium Hero Banner */}
      <section className="relative overflow-hidden rounded-3xl border border-slate-800 bg-gradient-to-b from-slate-900/90 via-slate-900/50 to-slate-950 p-6 md:p-12 glow-emerald">
        <div className="absolute top-0 right-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-teal-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 mb-4">
            <Flame className="w-3.5 h-3.5 animate-pulse" />
            Autonomous World Sports & News Intelligence
          </div>

          <h1 className="text-3xl sm:text-5xl md:text-6xl font-black text-white tracking-tight leading-[1.1]">
            THE PLAYBOOK OF <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-teal-300 to-sky-400">
              ALL WORLD GAMES
            </span>
          </h1>

          <p className="mt-4 text-slate-300 text-sm sm:text-base leading-relaxed max-w-2xl">
            Explore authentic rules, playing dimensions, equipment specifications, and tactical strategies — alongside breaking tournament dispatches and championship news from every corner of the earth.
          </p>

          {/* Search Box */}
          <form onSubmit={handleSearchSubmit} className="mt-6 flex items-center gap-2 max-w-xl">
            <div className="relative flex-1">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search any sport, game, or tournament news..."
                className="w-full pl-11 pr-4 py-3 bg-slate-950/80 border border-slate-700 rounded-2xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors shadow-inner"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => { setSearchQuery(''); fetchArticles(); }}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
            <button
              type="submit"
              className="px-5 py-3 rounded-2xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm transition-all shadow-lg shadow-emerald-500/25 flex items-center gap-1.5 shrink-0"
            >
              Search
            </button>
          </form>
        </div>
      </section>

      {/* Story Type Segmented Bar (Playbooks vs Breaking News) */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => setStoryType('All')}
          className={`flex items-center gap-2 px-4 py-2 rounded-2xl text-xs font-bold transition-all border ${
            storyType === 'All'
              ? 'bg-slate-100 text-slate-950 border-white shadow-lg'
              : 'bg-slate-900/80 text-slate-400 border-slate-800 hover:text-white'
          }`}
        >
          <Trophy className="w-3.5 h-3.5 text-amber-500" />
          All Coverage ({totalCount})
        </button>

        <button
          onClick={() => setStoryType('PLAYBOOK')}
          className={`flex items-center gap-2 px-4 py-2 rounded-2xl text-xs font-bold transition-all border ${
            storyType === 'PLAYBOOK'
              ? 'bg-emerald-500 text-slate-950 border-emerald-400 shadow-lg shadow-emerald-500/25'
              : 'bg-slate-900/80 text-slate-400 border-slate-800 hover:text-emerald-400'
          }`}
        >
          <BookOpen className="w-3.5 h-3.5" />
          Official Playbooks & Guides
        </button>

        <button
          onClick={() => setStoryType('NEWS')}
          className={`flex items-center gap-2 px-4 py-2 rounded-2xl text-xs font-bold transition-all border ${
            storyType === 'NEWS'
              ? 'bg-amber-500 text-slate-950 border-amber-400 shadow-lg shadow-amber-500/25'
              : 'bg-slate-900/80 text-slate-400 border-slate-800 hover:text-amber-400'
          }`}
        >
          <Radio className="w-3.5 h-3.5 animate-pulse text-rose-400" />
          Championship News & Dispatches
        </button>
      </div>

      {/* 3-Way Combinatorial Filters Arena */}
      <section className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 space-y-5">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2 text-sm font-bold text-white">
            <Filter className="w-4 h-4 text-emerald-400" />
            <span>Combinatorial Playbook Filters</span>
            {activeFiltersCount > 0 && (
              <span className="px-2 py-0.5 rounded-full text-[11px] bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30">
                {activeFiltersCount} Active
              </span>
            )}
          </div>

          <div className="flex items-center gap-3">
            {activeFiltersCount > 0 && (
              <button
                onClick={clearAllFilters}
                className="text-xs text-slate-400 hover:text-emerald-400 transition-colors flex items-center gap-1"
              >
                <X className="w-3.5 h-3.5" />
                Reset Filters
              </button>
            )}
            <div className="text-xs text-slate-400">
              Showing <span className="font-bold text-white">{articles.length}</span> of <span className="font-bold text-white">{totalCount}</span> stories
            </div>
          </div>
        </div>

        {/* 1. Global Regions Selector */}
        <div>
          <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
            <Globe2 className="w-3.5 h-3.5 text-emerald-400" />
            Filter by Region
          </label>
          <div className="flex flex-wrap gap-1.5">
            {REGIONS.map((region) => {
              const active = selectedRegion === region;
              return (
                <button
                  key={region}
                  onClick={() => setSelectedRegion(region)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
                    active
                      ? 'bg-emerald-500 text-slate-950 font-bold shadow-md shadow-emerald-500/20'
                      : 'bg-slate-800/70 text-slate-300 hover:bg-slate-800 hover:text-white border border-slate-700/50'
                  }`}
                >
                  {region}
                </button>
              );
            })}
          </div>
        </div>

        {/* 2. Sport Category Badges Grid */}
        <div>
          <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
            <Trophy className="w-3.5 h-3.5 text-emerald-400" />
            Filter by Sports Category
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
            <button
              onClick={() => setSelectedCategory('All')}
              className={`flex items-center gap-2 p-2 rounded-xl text-xs font-medium border text-left transition-all ${
                selectedCategory === 'All'
                  ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500 font-bold'
                  : 'bg-slate-800/40 text-slate-300 border-slate-800 hover:border-slate-700 hover:bg-slate-800'
              }`}
            >
              <Globe2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span className="truncate">All Categories</span>
            </button>

            {Object.entries(CATEGORY_CONFIG).map(([catName, config]) => {
              const IconComp = config.icon;
              const active = selectedCategory === catName;
              return (
                <button
                  key={catName}
                  onClick={() => setSelectedCategory(catName)}
                  className={`flex items-center gap-2 p-2 rounded-xl text-xs font-medium border text-left transition-all ${
                    active
                      ? `${config.bg} border-current font-bold`
                      : 'bg-slate-800/40 text-slate-300 border-slate-800 hover:border-slate-700 hover:bg-slate-800'
                  }`}
                >
                  <IconComp className="w-4 h-4 shrink-0" />
                  <span className="truncate">{catName}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* 3. Interactive Calendar Date Picker */}
        <div className="pt-2 border-t border-slate-800/60 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-400">
              <Calendar className="w-4 h-4 text-emerald-400" />
              <span>Publication Date:</span>
            </div>
            <div className="relative">
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="bg-slate-950 border border-slate-700 text-slate-200 text-xs px-3 py-1.5 rounded-xl focus:outline-none focus:border-emerald-500 cursor-pointer"
              />
            </div>
            {selectedDate && (
              <button
                onClick={() => setSelectedDate('')}
                className="text-xs text-rose-400 hover:underline flex items-center gap-1"
              >
                Clear Date
              </button>
            )}
          </div>

          <button
            onClick={fetchArticles}
            className="text-xs text-slate-400 hover:text-white flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh Feed
          </button>
        </div>
      </section>

      {/* Game Guides & News Grid */}
      <section>
        {loading ? (
          <div className="flex flex-col items-center justify-center py-24 text-slate-400 space-y-3">
            <RefreshCw className="w-8 h-8 text-emerald-400 animate-spin" />
            <p className="text-sm">Scouting world sports coverage...</p>
          </div>
        ) : articles.length === 0 ? (
          <div className="text-center py-20 bg-slate-900/30 border border-slate-800 rounded-3xl p-8 space-y-4">
            <Trophy className="w-12 h-12 text-slate-600 mx-auto" />
            <h3 className="text-lg font-bold text-white">No Stories Found</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto">
              No world game matched the current filter combination. Try clearing your filters or switching to "All Coverage".
            </p>
            <button
              onClick={clearAllFilters}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-emerald-500 text-slate-950 hover:bg-emerald-400 transition-colors"
            >
              Reset All Filters
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {articles.map((article) => {
              const catConfig = getCategoryConfig(article.category);
              const IconComp = catConfig.icon;
              const isNews = article.article_type === 'NEWS';

              return (
                <div
                  key={article.id}
                  onClick={() => setActiveArticle(article)}
                  className={`group relative bg-slate-900/80 border rounded-2xl overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl cursor-pointer flex flex-col ${
                    isNews
                      ? 'border-amber-500/30 hover:border-amber-500/60 hover:shadow-amber-500/10'
                      : 'border-slate-800 hover:border-emerald-500/50 hover:shadow-emerald-500/10'
                  }`}
                >
                  {/* Article Card Photo */}
                  <div className="relative h-48 w-full bg-slate-950 overflow-hidden">
                    <img
                      src={article.primary_image_url || 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?q=80&w=1200'}
                      alt={article.title}
                      className="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-500"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/20 to-transparent" />

                    {/* Top Badges */}
                    <div className="absolute top-3 left-3 right-3 flex items-center justify-between">
                      <div className="flex items-center gap-1.5">
                        {isNews ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-wider bg-amber-500 text-slate-950 shadow-md">
                            <Zap className="w-3 h-3 fill-current" />
                            Breaking News
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-wider bg-emerald-500 text-slate-950 shadow-md">
                            <BookOpen className="w-3 h-3" />
                            Playbook Guide
                          </span>
                        )}

                        <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold border backdrop-blur-md ${catConfig.bg}`}>
                          <IconComp className="w-3 h-3" />
                          {article.category}
                        </span>
                      </div>

                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40 backdrop-blur-md">
                        <Award className="w-3 h-3" />
                        {article.score?.toFixed(1)}/10
                      </span>
                    </div>

                    {/* Location Badge */}
                    <div className="absolute bottom-2.5 left-3 flex items-center gap-1 text-[11px] text-slate-300 font-medium bg-slate-950/70 backdrop-blur-sm px-2 py-0.5 rounded-md border border-slate-800">
                      <MapPin className="w-3 h-3 text-emerald-400" />
                      <span>{article.origin_country}</span>
                    </div>
                  </div>

                  {/* Article Details */}
                  <div className="p-5 flex-1 flex flex-col justify-between space-y-4">
                    <div>
                      <h3 className={`text-lg font-bold text-white transition-colors line-clamp-2 ${
                        isNews ? 'group-hover:text-amber-400' : 'group-hover:text-emerald-400'
                      }`}>
                        {article.title}
                      </h3>
                      <p className="mt-2 text-xs text-slate-400 line-clamp-3 leading-relaxed">
                        {article.summary}
                      </p>
                    </div>

                    <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5 text-emerald-400" />
                        {article.reading_time_minutes || 5} min read
                      </span>

                      <span className={`flex items-center gap-1 font-semibold group-hover:translate-x-1 transition-transform ${
                        isNews ? 'text-amber-400' : 'text-emerald-400'
                      }`}>
                        {isNews ? 'Read News Report' : 'Read Playbook'}
                        <ArrowRight className="w-3.5 h-3.5" />
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* Reader Modal */}
      {activeArticle && (
        <PlaybookModal
          article={activeArticle}
          onClose={() => setActiveArticle(null)}
        />
      )}
    </div>
  );
}
