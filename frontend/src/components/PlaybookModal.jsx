import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  X,
  Trophy,
  Globe2,
  Clock,
  Award,
  Shield,
  Layers,
  ExternalLink,
  MapPin,
  Calendar,
  CheckCircle2,
} from 'lucide-react';
import { getCategoryConfig } from '../utils/sportsIcons';

export default function PlaybookModal({ article, onClose }) {
  if (!article) return null;

  const catConfig = getCategoryConfig(article.category);
  const IconComponent = catConfig.icon;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 md:p-6 bg-slate-950/80 backdrop-blur-md overflow-y-auto">
      <div className="relative w-full max-w-4xl max-h-[92vh] bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-y-auto flex flex-col">
        {/* Sticky Stadium Modal Bar */}
        <div className="sticky top-0 z-20 flex items-center justify-between px-6 py-4 bg-slate-900/95 backdrop-blur-md border-b border-slate-800">
          <div className="flex items-center gap-3">
            <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${catConfig.bg}`}>
              <IconComponent className="w-3.5 h-3.5" />
              {article.category}
            </span>
            <span className="inline-flex items-center gap-1 text-xs text-slate-400 font-medium">
              <MapPin className="w-3 h-3 text-emerald-400" />
              {article.origin_country} ({article.origin_region})
            </span>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Hero / Action Image */}
        {article.primary_image_url && (
          <div className="relative w-full h-64 md:h-80 bg-slate-950 overflow-hidden shrink-0">
            <img
              src={article.primary_image_url}
              alt={article.title}
              className="w-full h-full object-cover object-center"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/40 to-transparent" />
            
            {/* Image Attribution Tag */}
            {article.image_attribution && (
              <div className="absolute bottom-3 left-6 right-6 flex items-center justify-between text-xs text-slate-400 bg-slate-950/70 backdrop-blur-sm px-3 py-1.5 rounded-lg border border-slate-800/80">
                <span className="truncate">{article.image_attribution}</span>
                <span className="shrink-0 font-medium text-emerald-400 ml-2">{article.image_license || 'Verified License'}</span>
              </div>
            )}
          </div>
        )}

        {/* Playbook Content */}
        <div className="p-6 md:p-8 space-y-6">
          {/* Title & Scoreboard Pill */}
          <div>
            <div className="flex flex-wrap items-center gap-2.5 mb-3">
              <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                <Award className="w-3.5 h-3.5" />
                Score: {article.score?.toFixed(1)}/10 Quality Gate
              </span>
              <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs text-slate-300 bg-slate-800/80">
                <Clock className="w-3.5 h-3.5 text-emerald-400" />
                {article.reading_time_minutes || 6} min read
              </span>
              <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs text-slate-400 bg-slate-800/50">
                <Calendar className="w-3.5 h-3.5" />
                {article.published_at ? new Date(article.published_at).toLocaleDateString() : 'Active Guide'}
              </span>
            </div>

            <h1 className="text-2xl md:text-4xl font-extrabold text-white tracking-tight">
              {article.title}
            </h1>
            <p className="mt-3 text-slate-400 text-sm md:text-base leading-relaxed italic border-l-2 border-emerald-500 pl-3">
              {article.summary}
            </p>
          </div>

          {/* Rendered 12 Sections with ReactMarkdown and RemarkGFM */}
          <div className="article-body text-slate-300">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                // Hide H1 because the title is prominently displayed in the header above
                h1: () => null,

                h2: ({ children }) => (
                  <h2 className="text-xl md:text-2xl font-bold text-emerald-400 mt-8 mb-3 flex items-center gap-2 border-b border-slate-800 pb-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shrink-0"></span>
                    <span>{children}</span>
                  </h2>
                ),

                h3: ({ children }) => (
                  <h3 className="text-lg font-semibold text-slate-200 mt-6 mb-2 text-emerald-300/90">
                    {children}
                  </h3>
                ),

                h4: ({ children }) => (
                  <h4 className="text-base font-semibold text-slate-300 mt-4 mb-2">
                    {children}
                  </h4>
                ),

                p: ({ children }) => (
                  <p className="text-slate-300 leading-relaxed my-3 text-base">
                    {children}
                  </p>
                ),

                strong: ({ children }) => (
                  <strong className="font-bold text-white">
                    {children}
                  </strong>
                ),

                em: ({ children }) => (
                  <em className="italic text-emerald-300/90 font-normal">
                    {children}
                  </em>
                ),

                ul: ({ children }) => (
                  <ul className="my-3 space-y-2 list-disc list-outside ml-6 text-slate-300">
                    {children}
                  </ul>
                ),

                ol: ({ children }) => (
                  <ol className="my-3 space-y-2 list-decimal list-outside ml-6 text-slate-300">
                    {children}
                  </ol>
                ),

                li: ({ children }) => (
                  <li className="text-slate-300 leading-relaxed my-1">
                    {children}
                  </li>
                ),

                table: ({ children }) => (
                  <div className="overflow-x-auto my-6 rounded-xl border border-slate-800 bg-slate-900/60 p-1 shadow-inner">
                    <table className="w-full text-left text-sm text-slate-300 border-collapse">
                      {children}
                    </table>
                  </div>
                ),

                thead: ({ children }) => (
                  <thead className="bg-slate-800/80 text-emerald-400 font-semibold border-b border-slate-700">
                    {children}
                  </thead>
                ),

                tbody: ({ children }) => (
                  <tbody className="divide-y divide-slate-800/50">
                    {children}
                  </tbody>
                ),

                tr: ({ children }) => (
                  <tr className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
                    {children}
                  </tr>
                ),

                th: ({ children }) => (
                  <th className="px-4 py-3 font-semibold text-emerald-400">
                    {children}
                  </th>
                ),

                td: ({ children }) => (
                  <td className="px-4 py-3 text-slate-300">
                    {children}
                  </td>
                ),

                blockquote: ({ children }) => (
                  <blockquote className="border-l-4 border-emerald-500/60 pl-4 py-2 my-4 italic text-slate-400 bg-slate-800/30 rounded-r-lg">
                    {children}
                  </blockquote>
                ),

                code: ({ children }) => (
                  <code className="bg-slate-800 text-emerald-300 px-1.5 py-0.5 rounded text-xs font-mono">
                    {children}
                  </code>
                ),

                hr: () => (
                  <hr className="my-6 border-slate-800" />
                ),
              }}
            >
              {article.content}
            </ReactMarkdown>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="sticky bottom-0 z-20 flex items-center justify-between px-6 py-4 bg-slate-900/95 backdrop-blur-md border-t border-slate-800">
          <div className="text-xs text-slate-500 flex items-center gap-1.5">
            <Shield className="w-3.5 h-3.5 text-emerald-500" />
            Audited & Certified by WorldGames AI Quality Engine
          </div>
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl text-sm font-semibold bg-emerald-500 hover:bg-emerald-400 text-slate-950 transition-colors shadow-lg shadow-emerald-500/20"
          >
            Close Guide
          </button>
        </div>
      </div>
    </div>
  );
}
