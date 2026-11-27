import React from 'react';
import { Clock, MapPin, Zap, ArrowUpRight, Calendar } from 'lucide-react';
import {
  FALLBACK_IMAGE,
  formatPublishedDate,
  formatRelativeTime,
  getSafeImageUrl,
  getTagBadgeStyle,
} from '../utils/formatters';

export default function HeroSplit({ articles = [], onSelectArticle }) {
  if (!articles || articles.length === 0) return null;

  const leadStory = articles[0];
  const wireStories = articles.slice(1, 7); // 5-6 recent headlines in Latest Wire
  const leadBadge = getTagBadgeStyle(leadStory);

  return (
    <section className="grid grid-cols-1 lg:grid-cols-10 gap-6 items-stretch">
      {/* Left 70% (7 cols on lg): 16:9 Featured Main Story Card */}
      <div
        onClick={() => onSelectArticle?.(leadStory)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && onSelectArticle?.(leadStory)}
        className="lg:col-span-7 group relative bg-[#151A23] border border-[#232A38] rounded-2xl overflow-hidden cursor-pointer arena-card-glow aspect-video"
      >
        <img
          src={getSafeImageUrl(leadStory.primary_image_url)}
          alt={leadStory.title}
          onError={(e) => {
            e.currentTarget.onerror = null;
            e.currentTarget.src = FALLBACK_IMAGE;
          }}
          className="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-500 ease-out"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#0B0E14] via-[#0B0E14]/50 to-transparent" />

        {/* Top Left Tag Badge */}
        <div className="absolute top-4 left-4 flex items-center gap-2">
          <span
            className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-display font-bold uppercase tracking-wider shadow-lg ${leadBadge.solidClasses}`}
          >
            {leadStory.article_type === 'NEWS' && (
              <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
            )}
            {leadBadge.label}
          </span>

          {leadStory.origin_country && (
            <span className="hidden sm:inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-medium bg-[#0B0E14]/80 text-[#F3F4F6] border border-[#232A38] backdrop-blur-md">
              <MapPin className="w-3 h-3 text-[#7C3AED]" />
              {leadStory.origin_country}
            </span>
          )}
        </div>

        {/* Overlay Headline & Meta inside 16:9 canvas bottom */}
        <div className="absolute bottom-0 left-0 right-0 p-5 sm:p-7">
          <h1 className="font-display text-2xl sm:text-3xl md:text-4xl font-bold text-[#F3F4F6] leading-tight group-hover:text-white transition-colors line-clamp-2">
            {leadStory.title}
          </h1>
          {leadStory.summary && (
            <p className="mt-2.5 text-sm sm:text-base text-[#9CA3AF] line-clamp-2 max-w-2xl">
              {leadStory.summary}
            </p>
          )}
          <div className="mt-4 flex flex-wrap items-center gap-3 text-xs text-[#9CA3AF]">
            <span className="inline-flex items-center gap-1.5 text-[#10B981] font-medium">
              <Clock className="w-3.5 h-3.5" />
              {leadStory.reading_time_minutes || 6} min read
            </span>
            <span>•</span>
            <span className="inline-flex items-center gap-1.5 text-[#F3F4F6]/90 font-medium">
              <Calendar className="w-3.5 h-3.5 text-[#7C3AED]" />
              {formatPublishedDate(leadStory.published_at || leadStory.created_at)}
            </span>
            <span>•</span>
            <span>{formatRelativeTime(leadStory.published_at || leadStory.created_at)}</span>
            <span className="ml-auto inline-flex items-center gap-1 font-display font-semibold text-[#7C3AED] group-hover:text-[#A78BFA]">
              Read Full Story
              <ArrowUpRight className="w-4 h-4" />
            </span>
          </div>
        </div>
      </div>

      {/* Right 30% (3 cols on lg): Scrollable "Latest Wire" matched precisely to hero height */}
      <div className="lg:col-span-3 relative">
        <aside className="lg:absolute lg:inset-0 bg-[#151A23] border border-[#232A38] rounded-2xl flex flex-col overflow-hidden">
          <div className="px-4 py-3.5 border-b border-[#232A38] flex items-center justify-between bg-[#151A23] shrink-0">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-[#7C3AED]" />
              <h2 className="font-display font-bold text-sm uppercase tracking-wider text-[#F3F4F6]">
                Latest Updates
              </h2>
            </div>
            <span className="text-[11px] font-mono text-[#10B981]">
              {wireStories.length} UPDATES
            </span>
          </div>

          <div className="flex-1 overflow-y-auto divide-y divide-[#232A38] max-h-[360px] lg:max-h-none">
            {wireStories.length === 0 ? (
              <div className="p-6 text-center text-xs text-[#9CA3AF]">
                No additional wire items in this filter.
              </div>
            ) : (
              wireStories.map((story) => {
                const badge = getTagBadgeStyle(story);
                return (
                  <button
                    key={story.id}
                    type="button"
                    onClick={() => onSelectArticle?.(story)}
                    className="w-full text-left p-4 hover:bg-[#1C2330] transition-colors group flex flex-col gap-1.5"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-display font-bold uppercase tracking-wider border ${badge.classes}`}
                      >
                        {badge.label}
                      </span>
                      <span className="text-[11px] font-mono text-[#9CA3AF] shrink-0">
                        {formatPublishedDate(story.published_at || story.created_at, false)} · {formatRelativeTime(story.published_at || story.created_at)}
                      </span>
                    </div>

                    <h3 className="font-display font-semibold text-sm text-[#F3F4F6] group-hover:text-[#A78BFA] transition-colors line-clamp-2 leading-snug">
                      {story.title}
                    </h3>

                    {story.origin_country && (
                      <div className="text-[11px] text-[#9CA3AF] truncate">
                        {story.origin_country}
                      </div>
                    )}
                  </button>
                );
              })
            )}
          </div>
        </aside>
      </div>
    </section>
  );
}
