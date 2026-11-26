import React from 'react';
import { AlertTriangle, RotateCcw, SearchX } from 'lucide-react';

export function HomeSkeleton() {
  return (
    <div className="space-y-10">
      {/* Split Hero Skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-10 gap-6">
        <div className="lg:col-span-7 aspect-video rounded-2xl border border-[#232A38] shimmer-bg" />
        <div className="lg:col-span-3 rounded-2xl border border-[#232A38] bg-[#151A23] p-4 space-y-4">
          <div className="h-5 w-32 rounded shimmer-bg" />
          {[...Array(5)].map((_, i) => (
            <div key={i} className="space-y-2 pt-3 border-t border-[#232A38]">
              <div className="h-3 w-20 rounded shimmer-bg" />
              <div className="h-4 w-full rounded shimmer-bg" />
              <div className="h-3 w-2/3 rounded shimmer-bg" />
            </div>
          ))}
        </div>
      </div>

      {/* 3-Column Card Grid Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, idx) => (
          <div
            key={idx}
            className="rounded-2xl border border-[#232A38] bg-[#151A23] overflow-hidden"
          >
            <div className="aspect-video w-full shimmer-bg" />
            <div className="p-5 space-y-3">
              <div className="h-3 w-24 rounded shimmer-bg" />
              <div className="h-5 w-full rounded shimmer-bg" />
              <div className="h-4 w-4/5 rounded shimmer-bg" />
              <div className="pt-3 border-t border-[#232A38] flex justify-between">
                <div className="h-3 w-16 rounded shimmer-bg" />
                <div className="h-3 w-20 rounded shimmer-bg" />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function ArticleDetailSkeleton() {
  return (
    <div className="max-w-3xl mx-auto space-y-6 pb-20">
      <div className="h-9 w-40 rounded-xl shimmer-bg" />
      <div className="flex gap-2">
        <div className="h-6 w-24 rounded-full shimmer-bg" />
        <div className="h-6 w-28 rounded-full shimmer-bg" />
      </div>
      <div className="h-10 w-full rounded-xl shimmer-bg" />
      <div className="h-10 w-3/4 rounded-xl shimmer-bg" />
      <div className="aspect-video w-full rounded-2xl border border-[#232A38] shimmer-bg" />
      <div className="space-y-3 pt-4">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="h-4 w-full rounded shimmer-bg" />
        ))}
      </div>
    </div>
  );
}

export function EmptyFilterState({ onReset }) {
  return (
    <div className="rounded-2xl border border-[#232A38] bg-[#151A23] p-12 text-center space-y-4">
      <div className="w-12 h-12 rounded-2xl bg-[#7C3AED]/15 border border-[#7C3AED]/35 flex items-center justify-center mx-auto">
        <SearchX className="w-6 h-6 text-[#7C3AED]" />
      </div>
      <h3 className="font-display text-xl font-bold text-[#F3F4F6]">
        No matching coverage found
      </h3>
      <p className="text-sm text-[#9CA3AF] max-w-md mx-auto">
        No articles matched your active filter or search combination. Reset your filters to browse all World Games stories.
      </p>
      <button
        type="button"
        onClick={onReset}
        className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#7C3AED] hover:bg-[#6D28D9] text-white text-xs font-display font-bold transition-colors shadow-lg shadow-[#7C3AED]/25"
      >
        <RotateCcw className="w-3.5 h-3.5" />
        Reset All Filters
      </button>
    </div>
  );
}

export function ApiErrorState({ message, onRetry }) {
  return (
    <div className="rounded-2xl border border-[#EF4444]/40 bg-[#151A23] p-10 text-center space-y-4">
      <div className="w-12 h-12 rounded-2xl bg-[#EF4444]/15 border border-[#EF4444]/35 flex items-center justify-center mx-auto">
        <AlertTriangle className="w-6 h-6 text-[#EF4444]" />
      </div>
      <h3 className="font-display text-xl font-bold text-[#F3F4F6]">
        Unable to Reach World Games Feed
      </h3>
      <p className="text-sm text-[#9CA3AF] max-w-md mx-auto">
        {message || 'The backend API did not respond as expected. Check that the server is running and try again.'}
      </p>
      <button
        type="button"
        onClick={onRetry}
        className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#10B981] hover:bg-[#059669] text-[#0B0E14] text-xs font-display font-bold transition-colors"
      >
        <RotateCcw className="w-3.5 h-3.5" />
        Retry Connection
      </button>
    </div>
  );
}
