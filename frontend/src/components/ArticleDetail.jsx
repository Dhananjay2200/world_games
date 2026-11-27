import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  ArrowLeft,
  Clock,
  MapPin,
  Calendar,
  Tag,
  ShieldCheck,
} from 'lucide-react';
import { fetchFeed } from '../services/api';
import {
  FALLBACK_IMAGE,
  formatPublishedDate,
  formatRelativeTime,
  getSafeImageUrl,
  getTagBadgeStyle,
  parseKeywords,
} from '../utils/formatters';
import { ArticleCard } from './NewsGrid';

export default function ArticleDetail({ article, onBack, onSelectArticle }) {
  const [scrollProgress, setScrollProgress] = useState(0);
  const [relatedArticles, setRelatedArticles] = useState([]);

  // Scroll to top when article changes & attach reading progress listener
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    setScrollProgress(0);

    const handleScroll = () => {
      const docHeight =
        document.documentElement.scrollHeight - document.documentElement.clientHeight;
      if (docHeight <= 0) {
        setScrollProgress(0);
        return;
      }
      const pct = Math.min(100, Math.max(0, (window.scrollY / docHeight) * 100));
      setScrollProgress(pct);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [article?.id, article?.slug]);

  // Load "More in Gaming" related cards
  useEffect(() => {
    if (!article) return;
    let active = true;

    async function loadRelated() {
      try {
        const res = await fetchFeed({
          category: article.category || undefined,
          limit: 6,
        });
        let items = (res?.articles || []).filter((a) => a.id !== article.id);

        if (items.length < 3) {
          const fallbackRes = await fetchFeed({ limit: 6 });
          const existingIds = new Set([article.id, ...items.map((i) => i.id)]);
          const extras = (fallbackRes?.articles || []).filter((a) => !existingIds.has(a.id));
          items = [...items, ...extras];
        }

        if (active) {
          setRelatedArticles(items.slice(0, 3));
        }
      } catch {
        if (active) setRelatedArticles([]);
      }
    }

    loadRelated();
    return () => {
      active = false;
    };
  }, [article?.id, article?.category]);

  if (!article) return null;

  const badge = getTagBadgeStyle(article);
  const keywords = parseKeywords(article.seo_keywords);
  const publishedDate = article.published_at || article.created_at;

  return (
    <div className="pb-20">
      {/* Top Fixed Electric Violet Reading Progress Bar */}
      <div className="fixed top-0 left-0 right-0 z-50 h-1 bg-[#151A23]/80">
        <div
          className="h-full bg-[#7C3AED] shadow-[0_0_12px_rgba(124,58,237,0.8)] transition-[width] duration-75"
          style={{ width: `${scrollProgress}%` }}
        />
      </div>

      {/* Distraction-Free Max-W-3XL Dark-Mode Reader */}
      <article className="max-w-3xl mx-auto">
        {/* Back Button */}
        <div className="mb-6">
          <button
            type="button"
            onClick={onBack}
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-[#151A23] border border-[#232A38] text-xs font-display font-semibold text-[#9CA3AF] hover:text-[#F3F4F6] hover:border-[#7C3AED]/60 transition-all"
          >
            <ArrowLeft className="w-4 h-4 text-[#7C3AED]" />
            Back to World Games
          </button>
        </div>

        {/* Meta Badges Row */}
        <div className="flex flex-wrap items-center gap-2.5 mb-4">
          <span
            className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-display font-bold uppercase tracking-wider border ${badge.classes}`}
          >
            {badge.label}
          </span>

          {article.origin_country && (
            <span className="inline-flex items-center gap-1 text-xs text-[#9CA3AF] bg-[#151A23] px-3 py-1 rounded-full border border-[#232A38]">
              <MapPin className="w-3.5 h-3.5 text-[#7C3AED]" />
              {article.origin_country}
              {article.origin_region ? ` · ${article.origin_region}` : ''}
            </span>
          )}
        </div>

        {/* Headline */}
        <h1 className="font-display text-3xl sm:text-4xl md:text-[42px] font-bold text-[#F3F4F6] leading-[1.15] tracking-tight">
          {article.title}
        </h1>

        {/* Sub-meta strip */}
        <div className="mt-4 flex flex-wrap items-center gap-4 text-xs text-[#9CA3AF] pb-6 border-b border-[#232A38]">
          <span className="inline-flex items-center gap-1.5 text-[#10B981] font-medium">
            <Clock className="w-3.5 h-3.5" />
            {article.reading_time_minutes || 6} min read
          </span>
          {publishedDate && (
            <span className="inline-flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-[#7C3AED]" />
              {formatPublishedDate(publishedDate)} ({formatRelativeTime(publishedDate)})
            </span>
          )}
          <span className="inline-flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-[#10B981]" />
            World Games Verified Desk
          </span>
        </div>

        {/* Lead Summary */}
        {article.summary && (
          <p className="mt-6 text-base sm:text-lg text-[#F3F4F6]/90 leading-relaxed border-l-4 border-[#7C3AED] pl-4 py-1 bg-[#151A23]/50 rounded-r-xl">
            {article.summary}
          </p>
        )}

        {/* Crisp Media Container */}
        <figure className="my-8 rounded-2xl overflow-hidden border border-[#232A38] bg-[#151A23] shadow-2xl">
          <div className="aspect-video w-full overflow-hidden bg-[#0B0E14]">
            <img
              src={getSafeImageUrl(article.primary_image_url)}
              alt={article.title}
              onError={(e) => {
                e.currentTarget.onerror = null;
                e.currentTarget.src = FALLBACK_IMAGE;
              }}
              className="w-full h-full object-cover object-center"
            />
          </div>
          {(article.image_caption || article.image_attribution) && (
            <figcaption className="px-4 py-3 text-xs text-[#9CA3AF] flex flex-wrap items-center justify-between gap-2 border-t border-[#232A38] bg-[#151A23]">
              <span className="truncate">
                {article.image_caption || article.image_attribution}
              </span>
              {article.image_license && (
                <span className="text-[#10B981] font-mono text-[11px] shrink-0">
                  {article.image_license}
                </span>
              )}
            </figcaption>
          )}
        </figure>

        {/* Full Article Markdown Body */}
        <div className="prose-arena text-[#F3F4F6]/90">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              h1: () => null,
              h2: ({ children }) => (
                <h2 className="font-display text-2xl font-bold text-[#F3F4F6] mt-10 mb-4 pb-2 border-b border-[#232A38] flex items-center gap-2.5">
                  <span className="w-2 h-2 rounded-full bg-[#10B981] shrink-0" />
                  <span>{children}</span>
                </h2>
              ),
              h3: ({ children }) => (
                <h3 className="font-display text-lg sm:text-xl font-semibold text-[#A78BFA] mt-7 mb-2.5">
                  {children}
                </h3>
              ),
              h4: ({ children }) => (
                <h4 className="font-display text-base font-semibold text-[#F3F4F6] mt-5 mb-2">
                  {children}
                </h4>
              ),
              p: ({ children }) => (
                <p className="text-[#D1D5DB] leading-[1.8] my-4 text-base sm:text-[17px]">
                  {children}
                </p>
              ),
              strong: ({ children }) => (
                <strong className="font-semibold text-[#F3F4F6]">{children}</strong>
              ),
              em: ({ children }) => (
                <em className="italic text-[#10B981]/90">{children}</em>
              ),
              ul: ({ children }) => (
                <ul className="my-4 space-y-2 list-disc list-outside ml-6 text-[#D1D5DB]">
                  {children}
                </ul>
              ),
              ol: ({ children }) => (
                <ol className="my-4 space-y-2 list-decimal list-outside ml-6 text-[#D1D5DB]">
                  {children}
                </ol>
              ),
              li: ({ children }) => (
                <li className="leading-relaxed text-base">{children}</li>
              ),
              table: ({ children }) => (
                <div className="overflow-x-auto my-7 rounded-xl border border-[#232A38] bg-[#151A23]">
                  <table className="w-full text-left text-sm text-[#D1D5DB] border-collapse">
                    {children}
                  </table>
                </div>
              ),
              thead: ({ children }) => (
                <thead className="bg-[#1C2330] text-[#10B981] font-display font-semibold border-b border-[#232A38]">
                  {children}
                </thead>
              ),
              tbody: ({ children }) => (
                <tbody className="divide-y divide-[#232A38]">{children}</tbody>
              ),
              tr: ({ children }) => (
                <tr className="hover:bg-[#1C2330]/60 transition-colors">{children}</tr>
              ),
              th: ({ children }) => (
                <th className="px-4 py-3 font-semibold text-[#10B981]">{children}</th>
              ),
              td: ({ children }) => (
                <td className="px-4 py-3 text-[#D1D5DB]">{children}</td>
              ),
              blockquote: ({ children }) => (
                <blockquote className="border-l-4 border-[#7C3AED] pl-4 py-2 my-5 italic text-[#9CA3AF] bg-[#151A23] rounded-r-xl">
                  {children}
                </blockquote>
              ),
              code: ({ children }) => (
                <code className="bg-[#151A23] border border-[#232A38] text-[#10B981] px-1.5 py-0.5 rounded text-xs font-mono">
                  {children}
                </code>
              ),
              hr: () => <hr className="my-8 border-[#232A38]" />,
            }}
          >
            {article.content}
          </ReactMarkdown>
        </div>

        {/* Tags List */}
        {keywords.length > 0 && (
          <div className="mt-10 pt-6 border-t border-[#232A38]">
            <div className="flex items-center gap-2 text-xs font-display font-bold uppercase tracking-wider text-[#9CA3AF] mb-3">
              <Tag className="w-3.5 h-3.5 text-[#7C3AED]" />
              <span>Topics & Tags</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {keywords.map((kw, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 rounded-lg text-xs font-medium bg-[#151A23] border border-[#232A38] text-[#9CA3AF] hover:text-[#F3F4F6] hover:border-[#7C3AED]/50 transition-colors"
                >
                  #{kw}
                </span>
              ))}
            </div>
          </div>
        )}
      </article>

      {/* "More in Gaming" Related Stories Section */}
      {relatedArticles.length > 0 && (
        <section className="max-w-7xl mx-auto mt-16 pt-10 border-t border-[#232A38] space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="font-display text-xl sm:text-2xl font-bold text-[#F3F4F6] flex items-center gap-2.5">
              <span className="w-1.5 h-6 rounded-full bg-[#10B981]" />
              More in Gaming
            </h2>
            <button
              type="button"
              onClick={onBack}
              className="text-xs font-display font-semibold text-[#7C3AED] hover:text-[#A78BFA]"
            >
              View All Stories →
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {relatedArticles.map((rel) => (
              <ArticleCard
                key={rel.id}
                article={rel}
                onSelect={onSelectArticle}
              />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
