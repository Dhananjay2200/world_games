import React from 'react';
import { Clock, MapPin, ArrowUpRight } from 'lucide-react';
import {
  FALLBACK_IMAGE,
  formatRelativeTime,
  getSafeImageUrl,
  getTagBadgeStyle,
} from '../utils/formatters';

export function ArticleCard({ article, onSelect }) {
  const badge = getTagBadgeStyle(article);

  return (
    <article
      onClick={() => onSelect?.(article)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onSelect?.(article)}
      className="group bg-[#151A23] border border-[#232A38] rounded-2xl overflow-hidden cursor-pointer arena-card-glow flex flex-col"
    >
      {/* 16:9 Thumbnail */}
      <div className="relative aspect-video w-full bg-[#0B0E14] overflow-hidden">
        <img
          src={getSafeImageUrl(article.primary_image_url)}
          alt={article.title}
          loading="lazy"
          onError={(e) => {
            e.currentTarget.onerror = null;
            e.currentTarget.src = FALLBACK_IMAGE;
          }}
          className="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-500 ease-out"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#151A23] via-transparent to-black/25" />

        {/* Color-Coded Tag Pill */}
        <div className="absolute top-3 left-3 flex items-center gap-1.5">
          <span
            className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[10px] font-display font-bold uppercase tracking-wider border backdrop-blur-md ${badge.classes}`}
          >
            {article.article_type === 'NEWS' && (
              <span className="w-1.5 h-1.5 rounded-full bg-[#EF4444] animate-pulse" />
            )}
            {badge.label}
          </span>
        </div>
      </div>

      {/* Card Body */}
      <div className="p-5 flex-1 flex flex-col justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-[11px] text-[#9CA3AF] mb-2">
            {article.origin_country && (
              <span className="inline-flex items-center gap-1 truncate">
                <MapPin className="w-3 h-3 text-[#7C3AED] shrink-0" />
                <span className="truncate">{article.origin_country}</span>
              </span>
            )}
            {article.origin_country && <span>•</span>}
            <span className="shrink-0 font-mono">
              {formatRelativeTime(article.published_at || article.created_at)}
            </span>
          </div>

          <h3 className="font-display text-lg font-bold text-[#F3F4F6] group-hover:text-[#A78BFA] transition-colors line-clamp-2 leading-snug">
            {article.title}
          </h3>

          {article.summary && (
            <p className="mt-2 text-xs sm:text-sm text-[#9CA3AF] line-clamp-2 leading-relaxed">
              {article.summary}
            </p>
          )}
        </div>

        {/* Card Footer */}
        <div className="pt-3 border-t border-[#232A38] flex items-center justify-between text-xs text-[#9CA3AF]">
          <span className="inline-flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-[#10B981]" />
            {article.reading_time_minutes || 6} min read
          </span>

          <span className="inline-flex items-center gap-1 font-display font-semibold text-[#7C3AED] group-hover:translate-x-0.5 transition-transform">
            {article.article_type === 'NEWS' ? 'Read Report' : 'Read Guide'}
            <ArrowUpRight className="w-3.5 h-3.5" />
          </span>
        </div>
      </div>
    </article>
  );
}

export default function NewsGrid({ articles = [], onSelectArticle, heading = 'All Stories' }) {
  if (!articles || articles.length === 0) return null;

  return (
    <section className="space-y-5">
      <div className="flex items-center justify-between border-b border-[#232A38] pb-3">
        <h2 className="font-display text-xl font-bold text-[#F3F4F6] flex items-center gap-2.5">
          <span className="w-1.5 h-5 rounded-full bg-[#7C3AED]" />
          {heading}
        </h2>
        <span className="text-xs font-mono text-[#9CA3AF]">
          {articles.length} {articles.length === 1 ? 'STORY' : 'STORIES'}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {articles.map((article) => (
          <ArticleCard
            key={article.id}
            article={article}
            onSelect={onSelectArticle}
          />
        ))}
      </div>
    </section>
  );
}
