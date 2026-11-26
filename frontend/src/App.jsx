import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Gamepad2, ArrowLeft, Zap, Shield } from 'lucide-react';
import {
  fetchFeed,
  fetchArticleBySlug,
  fetchTaxonomy,
  fetchSystemStats,
} from './services/api';
import BreakingTicker from './components/BreakingTicker';
import Navbar from './components/Navbar';
import HeroSplit from './components/HeroSplit';
import NewsGrid from './components/NewsGrid';
import ArticleDetail from './components/ArticleDetail';
import AdminPortal from './components/AdminPortal';
import {
  HomeSkeleton,
  ArticleDetailSkeleton,
  EmptyFilterState,
  ApiErrorState,
} from './components/Skeletons';
import { shortenCategory } from './utils/formatters';

function parseRoute(pathname) {
  const clean = pathname.replace(/\/+$/, '') || '/';
  if (clean === '/admin' || clean.startsWith('/admin/')) {
    return { view: 'admin', slug: null };
  }
  if (clean.startsWith('/article/')) {
    const slug = decodeURIComponent(clean.replace('/article/', ''));
    return { view: 'article', slug };
  }
  return { view: 'home', slug: null };
}

export default function App() {
  const [route, setRoute] = useState(() => parseRoute(window.location.pathname));

  // Public Feed & Taxonomy State
  const [articles, setArticles] = useState([]);
  const [tickerArticles, setTickerArticles] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [categories, setCategories] = useState([]);
  const [regions, setRegions] = useState([]);

  // Filters
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedRegion, setSelectedRegion] = useState('All');
  const [selectedType, setSelectedType] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [appliedSearch, setAppliedSearch] = useState('');

  // Loading & Error States
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Article Detail State
  const [activeArticle, setActiveArticle] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState('');

  // Admin Stats (only actively fetched when on /admin)
  const [stats, setStats] = useState(null);

  // Sync browser Back / Forward navigation
  useEffect(() => {
    const onPopState = () => {
      setRoute(parseRoute(window.location.pathname));
    };
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  const navigate = useCallback((path) => {
    if (window.location.pathname !== path) {
      window.history.pushState({}, '', path);
    }
    setRoute(parseRoute(path));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  // Load Taxonomy & Ticker Headlines once on mount
  useEffect(() => {
    let active = true;
    async function initMeta() {
      try {
        const [tax, tickerData] = await Promise.all([
          fetchTaxonomy().catch(() => null),
          fetchFeed({ limit: 5 }).catch(() => null),
        ]);
        if (!active) return;
        if (tax) {
          setCategories(tax.categories || []);
          setRegions(tax.regions || []);
        }
        if (tickerData?.articles) {
          setTickerArticles(tickerData.articles);
        }
      } catch {
        // Non-fatal metadata fetch
      }
    }
    initMeta();
    return () => {
      active = false;
    };
  }, []);

  // Load Public Feed whenever filters change (supports silent background updates)
  const loadFeed = useCallback(async ({ silent = false } = {}) => {
    if (!silent) {
      setLoading(true);
      setError('');
    }
    try {
      const data = await fetchFeed({
        category: selectedCategory,
        region: selectedRegion,
        articleType: selectedType,
        search: appliedSearch,
        limit: 60,
        offset: 0,
      });
      setArticles(data.articles || []);
      setTotalCount(data.total || 0);
    } catch (err) {
      if (!silent) {
        setError(err.message || 'Failed to load articles from backend.');
      }
    } finally {
      if (!silent) {
        setLoading(false);
      }
    }
  }, [selectedCategory, selectedRegion, selectedType, appliedSearch]);

  const refreshTicker = useCallback(async () => {
    try {
      const tickerData = await fetchFeed({ limit: 5 });
      if (tickerData?.articles) {
        setTickerArticles(tickerData.articles);
      }
    } catch {
      // Ignore silent ticker sync failures
    }
  }, []);

  useEffect(() => {
    if (route.view === 'home') {
      loadFeed({ silent: false });
    }
  }, [route.view, loadFeed]);

  // Live Auto-Refresh on Public Site when new articles are published in background or another tab
  const lastPublicStatsSig = useRef(null);

  useEffect(() => {
    if (route.view === 'admin') return;

    const syncPublicUpdates = async () => {
      try {
        const s = await fetchSystemStats();
        const sig = `${s?.total_articles ?? 0}:${s?.total_playbooks ?? 0}:${s?.total_news ?? 0}`;
        if (lastPublicStatsSig.current === null) {
          lastPublicStatsSig.current = sig;
          return;
        }
        if (lastPublicStatsSig.current !== sig) {
          lastPublicStatsSig.current = sig;
          refreshTicker();
          if (route.view === 'home') {
            loadFeed({ silent: true });
          }
        }
      } catch {
        // Silent polling failure
      }
    };

    syncPublicUpdates();
    const pollId = setInterval(syncPublicUpdates, 8000);

    let channel = null;
    if (typeof BroadcastChannel !== 'undefined') {
      channel = new BroadcastChannel('worldgames_updates');
      channel.onmessage = (event) => {
        if (event?.data?.type === 'ARTICLES_UPDATED') {
          refreshTicker();
          if (route.view === 'home') {
            loadFeed({ silent: true });
          }
        }
      };
    }

    const onVisibility = () => {
      if (document.visibilityState === 'visible') {
        syncPublicUpdates();
      }
    };
    document.addEventListener('visibilitychange', onVisibility);

    return () => {
      clearInterval(pollId);
      if (channel) channel.close();
      document.removeEventListener('visibilitychange', onVisibility);
    };
  }, [route.view, loadFeed, refreshTicker]);

  // Load Article Detail by slug when on /article/:slug
  const loadArticleDetail = useCallback(
    async (slug) => {
      if (!slug) return;
      const cached =
        articles.find((a) => a.slug === slug) ||
        tickerArticles.find((a) => a.slug === slug);

      if (cached && cached.content) {
        setActiveArticle(cached);
        setDetailError('');
        setDetailLoading(false);
        return;
      }

      setDetailLoading(true);
      setDetailError('');
      try {
        const fullArticle = await fetchArticleBySlug(slug);
        setActiveArticle(fullArticle);
      } catch (err) {
        setDetailError(err.message || 'Article not found.');
        setActiveArticle(null);
      } finally {
        setDetailLoading(false);
      }
    },
    [articles, tickerArticles]
  );

  useEffect(() => {
    if (route.view === 'article' && route.slug) {
      loadArticleDetail(route.slug);
    }
  }, [route.view, route.slug, loadArticleDetail]);

  // Load System Stats only when accessing /admin directly
  const loadStats = useCallback(async () => {
    try {
      const data = await fetchSystemStats();
      setStats(data);
    } catch {
      // Admin portal handles connection state gracefully
    }
  }, []);

  useEffect(() => {
    if (route.view === 'admin') {
      loadStats();
      const interval = setInterval(loadStats, 5000);
      return () => clearInterval(interval);
    }
  }, [route.view, loadStats]);

  // Handlers
  const openArticle = (article) => {
    if (!article?.slug) return;
    setActiveArticle(article);
    navigate(`/article/${encodeURIComponent(article.slug)}`);
  };

  const resetFilters = () => {
    setSelectedCategory('All');
    setSelectedRegion('All');
    setSelectedType('All');
    setSearchQuery('');
    setAppliedSearch('');
    if (route.view !== 'home') {
      navigate('/');
    }
  };

  const handleSearchSubmit = (e, overrideQuery) => {
    if (e) e.preventDefault();
    const nextSearch = overrideQuery !== undefined ? overrideQuery : searchQuery;
    setAppliedSearch(nextSearch.trim());
    if (route.view !== 'home') {
      navigate('/');
    }
  };

  // Hidden /admin Portal Route (accessible strictly via /admin URL, zero links in public UI)
  if (route.view === 'admin') {
    return (
      <div className="min-h-screen bg-[#0B0E14] text-[#F3F4F6] flex flex-col">
        <header className="sticky top-0 z-40 border-b border-[#232A38] bg-[#0B0E14]/90 backdrop-blur-xl">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-[#7C3AED]/20 border border-[#7C3AED]/50 flex items-center justify-center">
                <Shield className="w-4 h-4 text-[#7C3AED]" />
              </div>
              <div>
                <span className="font-display font-bold text-base text-[#F3F4F6]">
                  World Games · Admin Console
                </span>
                <p className="text-[11px] text-[#9CA3AF]">Editorial & Autonomous Pipeline Desk</p>
              </div>
            </div>

            <button
              type="button"
              onClick={() => navigate('/')}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-[#151A23] border border-[#232A38] text-xs font-display font-semibold text-[#F3F4F6] hover:border-[#10B981]/60 transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5 text-[#10B981]" />
              Back to Public Site
            </button>
          </div>
        </header>

        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-8">
          <AdminPortal stats={stats} onRefreshStats={loadStats} />
        </main>
      </div>
    );
  }

  const isFiltered =
    selectedCategory !== 'All' ||
    selectedRegion !== 'All' ||
    selectedType !== 'All' ||
    Boolean(appliedSearch);

  const gridArticles = isFiltered
    ? articles
    : articles.length > 7
    ? articles.slice(7)
    : articles;

  const gridHeading = isFiltered
    ? [
        selectedType === 'NEWS' ? 'Breaking News' : null,
        selectedCategory !== 'All' ? shortenCategory(selectedCategory) : null,
        selectedRegion !== 'All' ? selectedRegion : null,
        appliedSearch ? `"${appliedSearch}"` : null,
      ]
        .filter(Boolean)
        .join(' · ')
    : 'More Dispatches & Guides';

  return (
    <div className="min-h-screen bg-[#0B0E14] text-[#F3F4F6] flex flex-col">
      {/* 1. Top Breaking / Trending Ticker */}
      <BreakingTicker articles={tickerArticles} onSelectArticle={openArticle} />

      {/* 2. Sticky Glassmorphic Navbar & Platform/Genre Filter Pills */}
      <Navbar
        onGoHome={resetFilters}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        onSearchSubmit={handleSearchSubmit}
        categories={categories}
        regions={regions}
        selectedCategory={selectedCategory}
        onSelectCategory={(cat) => {
          setSelectedCategory(cat);
          if (route.view !== 'home') navigate('/');
        }}
        selectedRegion={selectedRegion}
        onSelectRegion={(reg) => {
          setSelectedRegion(reg);
          if (route.view !== 'home') navigate('/');
        }}
        selectedType={selectedType}
        onSelectType={(tp) => {
          setSelectedType(tp);
          if (route.view !== 'home') navigate('/');
        }}
        totalCount={totalCount}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-8 pb-14">
        {route.view === 'article' ? (
          detailLoading ? (
            <ArticleDetailSkeleton />
          ) : detailError ? (
            <ApiErrorState
              message={detailError}
              onRetry={() => loadArticleDetail(route.slug)}
            />
          ) : (
            <ArticleDetail
              article={activeArticle}
              onBack={() => navigate('/')}
              onSelectArticle={openArticle}
            />
          )
        ) : loading ? (
          <HomeSkeleton />
        ) : error ? (
          <ApiErrorState message={error} onRetry={loadFeed} />
        ) : articles.length === 0 ? (
          <EmptyFilterState onReset={resetFilters} />
        ) : (
          <div className="space-y-12">
            {/* 3. Split Hero Layout (70% Featured 16:9 / 30% Latest Wire) when unfiltered */}
            {!isFiltered && (
              <HeroSplit articles={articles} onSelectArticle={openArticle} />
            )}

            {/* 4. 3-Column Responsive News & Guides Grid */}
            <NewsGrid
              articles={gridArticles}
              onSelectArticle={openArticle}
              heading={gridHeading}
            />
          </div>
        )}
      </main>

      {/* Clean Public Footer (Zero Admin Links) */}
      <footer className="border-t border-[#232A38] bg-[#0B0E14] py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-[#9CA3AF]">
          <div className="flex items-center gap-2.5">
            <Gamepad2 className="w-4 h-4 text-[#7C3AED]" />
            <span className="font-display font-bold text-[#F3F4F6]">World Games</span>
            <span>— Global Gaming, Esports & Competitive Play</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-1.5 text-[#10B981]">
              <Zap className="w-3.5 h-3.5" />
              Live Sports Feed
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
