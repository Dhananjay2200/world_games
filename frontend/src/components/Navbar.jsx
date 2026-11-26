import React from 'react';
import { Gamepad2, Search, X, Globe2, Radio, ChevronDown } from 'lucide-react';
import { shortenCategory } from '../utils/formatters';

export default function Navbar({
  onGoHome,
  searchQuery,
  setSearchQuery,
  onSearchSubmit,
  categories = [],
  regions = [],
  selectedCategory,
  onSelectCategory,
  selectedRegion,
  onSelectRegion,
  selectedType,
  onSelectType,
  totalCount = 0,
}) {
  // Dynamically construct quick-filter pills grounded in real backend taxonomy + Breaking News
  const preferredOrder = [
    'Esports & Competitive Digital Gaming',
    'Combat Sports & Martial Arts',
    'Field & Team Ball Sports',
    'Board, Tile & Strategy Games',
    'Mind Sports & Tabletop Games',
    'Indigenous, Folk & Traditional Games',
  ];

  const sortedCategories = [
    ...preferredOrder.filter((c) => categories.includes(c)),
    ...categories.filter((c) => !preferredOrder.includes(c)),
  ].slice(0, 6);

  const isAllActive =
    selectedCategory === 'All' &&
    selectedType === 'All' &&
    selectedRegion === 'All' &&
    !searchQuery;

  return (
    <header className="sticky top-0 z-40 w-full bg-[#0B0E14]/85 backdrop-blur-xl border-b border-[#232A38]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Top Row: Brand + Search + Live Count (NO Admin button) */}
        <div className="h-16 flex items-center justify-between gap-4">
          {/* Brand Logo */}
          <button
            type="button"
            onClick={onGoHome}
            className="flex items-center gap-3 group shrink-0 text-left"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#7C3AED] to-[#10B981] p-[1.5px] shadow-lg shadow-[#7C3AED]/20 group-hover:scale-105 transition-transform">
              <div className="w-full h-full bg-[#0B0E14] rounded-[10px] flex items-center justify-center">
                <Gamepad2 className="w-5 h-5 text-[#10B981] group-hover:text-[#7C3AED] transition-colors" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-display font-bold text-lg sm:text-xl tracking-tight text-[#F3F4F6]">
                  WORLD<span className="text-[#7C3AED]">GAMES</span>
                </span>
                <span className="hidden sm:inline-block px-1.5 py-0.5 rounded text-[10px] font-display font-bold uppercase tracking-wider bg-[#10B981]/15 text-[#10B981] border border-[#10B981]/30">
                  LIVE
                </span>
              </div>
              <p className="text-[11px] text-[#9CA3AF] hidden sm:block">
                Gaming, Esports & Global Competitive Play
              </p>
            </div>
          </button>

          {/* Search Input */}
          <form onSubmit={onSearchSubmit} className="flex-1 max-w-md relative">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#9CA3AF] pointer-events-none" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search games, esports, tournaments..."
              className="w-full pl-10 pr-9 py-2 bg-[#151A23] border border-[#232A38] rounded-xl text-sm text-[#F3F4F6] placeholder-[#9CA3AF]/70 focus:outline-none focus:border-[#7C3AED] focus:ring-1 focus:ring-[#7C3AED]/40 transition-all"
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => {
                  setSearchQuery('');
                  onSearchSubmit?.(null, '');
                }}
                aria-label="Clear search"
                className="absolute right-3 top-1/2 -translate-y-1/2 text-[#9CA3AF] hover:text-[#F3F4F6]"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </form>

          {/* Subtle Region Selector + Story Count */}
          <div className="hidden md:flex items-center gap-3 shrink-0">
            {regions.length > 0 && (
              <div className="relative">
                <Globe2 className="w-3.5 h-3.5 text-[#10B981] absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                <select
                  value={selectedRegion}
                  onChange={(e) => onSelectRegion(e.target.value)}
                  aria-label="Filter by region"
                  className="appearance-none pl-8 pr-7 py-1.5 rounded-xl bg-[#151A23] border border-[#232A38] text-xs font-medium text-[#F3F4F6] focus:outline-none focus:border-[#7C3AED] cursor-pointer"
                >
                  <option value="All">All Regions</option>
                  {regions.map((r) => (
                    <option key={r} value={r}>
                      {r}
                    </option>
                  ))}
                </select>
                <ChevronDown className="w-3.5 h-3.5 text-[#9CA3AF] absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              </div>
            )}

            <div className="px-3 py-1.5 rounded-xl bg-[#151A23] border border-[#232A38] text-xs font-display text-[#9CA3AF]">
              <span className="text-[#10B981] font-bold">{totalCount}</span> Stories
            </div>
          </div>
        </div>

        {/* Second Row: Quick Filter Pills (Dynamically matched to backend categories + Breaking News) */}
        <div className="pb-3 pt-1 flex items-center gap-2 overflow-x-auto no-scrollbar">
          <button
            type="button"
            onClick={() => {
              onSelectCategory('All');
              onSelectType('All');
              onSelectRegion('All');
            }}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-display font-semibold shrink-0 transition-all border ${
              isAllActive
                ? 'bg-[#7C3AED] text-white border-[#7C3AED] shadow-md shadow-[#7C3AED]/25'
                : 'bg-[#151A23] text-[#9CA3AF] border-[#232A38] hover:text-[#F3F4F6] hover:border-[#7C3AED]/50'
            }`}
          >
            All
          </button>

          {/* Breaking News / Dispatches Toggle Pill */}
          <button
            type="button"
            onClick={() => {
              onSelectType(selectedType === 'NEWS' ? 'All' : 'NEWS');
            }}
            className={`inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-display font-semibold shrink-0 transition-all border ${
              selectedType === 'NEWS'
                ? 'bg-[#EF4444] text-white border-[#EF4444] shadow-md shadow-[#EF4444]/25'
                : 'bg-[#151A23] text-[#9CA3AF] border-[#232A38] hover:text-[#F3F4F6] hover:border-[#EF4444]/50'
            }`}
          >
            <Radio className="w-3 h-3" />
            <span>Breaking News</span>
          </button>

          {/* Dynamic Category Pills from Backend */}
          {sortedCategories.map((cat) => {
            const active = selectedCategory === cat;
            return (
              <button
                key={cat}
                type="button"
                onClick={() => onSelectCategory(active ? 'All' : cat)}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-display font-semibold shrink-0 transition-all border ${
                  active
                    ? 'bg-[#7C3AED] text-white border-[#7C3AED] shadow-md shadow-[#7C3AED]/25'
                    : 'bg-[#151A23] text-[#9CA3AF] border-[#232A38] hover:text-[#F3F4F6] hover:border-[#7C3AED]/50'
                }`}
              >
                {shortenCategory(cat)}
              </button>
            );
          })}

          {/* Full Category Dropdown for Remaining Categories */}
          {categories.length > sortedCategories.length && (
            <div className="relative shrink-0">
              <select
                value={categories.includes(selectedCategory) ? selectedCategory : 'All'}
                onChange={(e) => onSelectCategory(e.target.value)}
                aria-label="More categories"
                className="appearance-none pl-3 pr-7 py-1.5 rounded-lg bg-[#151A23] border border-[#232A38] text-xs font-display font-semibold text-[#9CA3AF] hover:text-[#F3F4F6] focus:outline-none focus:border-[#7C3AED] cursor-pointer"
              >
                <option value="All">More Genres...</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-[#9CA3AF] absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
