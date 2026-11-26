import React from 'react';
import { ChevronRight } from 'lucide-react';
import { formatRelativeTime } from '../utils/formatters';

export default function BreakingTicker({ articles = [], onSelectArticle }) {
  const headlines = articles.slice(0, 5);
  if (headlines.length === 0) return null;

  return (
    <div className="w-full bg-[#080A0F] border-b border-[#232A38] text-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-9 flex items-center gap-3 overflow-hidden">
        {/* Live / Breaking Indicator */}
        <div className="flex items-center gap-2 shrink-0 pr-3 border-r border-[#232A38]">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#EF4444] opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-[#EF4444]"></span>
          </span>
          <span className="font-display font-bold uppercase tracking-wider text-[11px] text-[#EF4444]">
            LIVE
          </span>
        </div>

        {/* Clickable Latest Headlines Strip */}
        <div className="flex items-center gap-5 overflow-x-auto no-scrollbar py-1">
          {headlines.map((item, idx) => (
            <button
              key={item.id || idx}
              type="button"
              onClick={() => onSelectArticle?.(item)}
              className="group flex items-center gap-2 shrink-0 text-[#9CA3AF] hover:text-[#F3F4F6] transition-colors text-left"
            >
              <span className="text-[10px] font-mono text-[#7C3AED] font-semibold">
                {formatRelativeTime(item.published_at || item.created_at)}
              </span>
              <span className="truncate max-w-[260px] sm:max-w-[340px] font-medium group-hover:text-white">
                {item.title}
              </span>
              <ChevronRight className="w-3 h-3 text-[#7C3AED] opacity-0 group-hover:opacity-100 transition-opacity" />
              {idx < headlines.length - 1 && (
                <span className="text-[#232A38] ml-2 select-none">•</span>
              )}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
