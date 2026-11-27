/**
 * Shared formatting, image fallback, and badge helpers for World Games UI.
 */

export const FALLBACK_IMAGE =
  "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 675'%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0' y1='0' x2='1' y2='1'%3E%3Cstop offset='0%25' stop-color='%230B0E14'/%3E%3Cstop offset='50%25' stop-color='%23151A23'/%3E%3Cstop offset='100%25' stop-color='%231E1B4B'/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width='1200' height='675' fill='url(%23g)'/%3E%3Ccircle cx='600' cy='338' r='160' fill='%237C3AED' fill-opacity='0.14'/%3E%3Ctext x='600' y='348' text-anchor='middle' fill='%239CA3AF' font-family='sans-serif' font-size='28' font-weight='700'%3EWORLD GAMES%3C/text%3E%3C/svg%3E";

export function getSafeImageUrl(url) {
  if (!url || typeof url !== 'string' || !url.trim()) return FALLBACK_IMAGE;
  return url;
}

export function parseUtcDate(dateInput) {
  if (!dateInput) return null;
  if (dateInput instanceof Date) {
    return Number.isNaN(dateInput.getTime()) ? null : dateInput;
  }
  const str = String(dateInput).trim();
  if (!str) return null;
  // Backend emits naive UTC ISO timestamps (datetime.utcnow().isoformat()); append 'Z' when missing
  const hasZone = /([zZ]|[+-]\d{2}:\d{2})$/.test(str);
  const parsed = new Date(hasZone ? str : `${str}Z`);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

export function formatPublishedDate(dateInput, includeYear = true) {
  const parsed = parseUtcDate(dateInput);
  if (!parsed) return 'Recent';
  return parsed.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    ...(includeYear ? { year: 'numeric' } : {}),
  });
}

export function formatRelativeTime(dateInput) {
  const parsed = parseUtcDate(dateInput);
  if (!parsed) return 'Recent';

  const diffSeconds = Math.max(0, Math.floor((Date.now() - parsed.getTime()) / 1000));
  if (diffSeconds < 60) return 'Just now';
  const diffMins = Math.floor(diffSeconds / 60);
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 30) return `${diffDays}d ago`;
  return formatPublishedDate(parsed, true);
}

export function parseKeywords(seoKeywords) {
  if (!seoKeywords) return [];
  if (Array.isArray(seoKeywords)) return seoKeywords.filter(Boolean);
  if (typeof seoKeywords === 'string') {
    const trimmed = seoKeywords.trim();
    if (!trimmed) return [];
    if (trimmed.startsWith('[')) {
      try {
        const parsed = JSON.parse(trimmed);
        if (Array.isArray(parsed)) return parsed.filter(Boolean);
      } catch {
        // Fallback to comma split
      }
    }
    return trimmed
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);
  }
  return [];
}

/**
 * Maps backend article_type & category to crisp, color-coded UI badges.
 */
export function getTagBadgeStyle(article) {
  const type = (article?.article_type || '').toUpperCase();
  const category = (article?.category || '').toLowerCase();

  if (type === 'NEWS') {
    return {
      label: 'Breaking News',
      classes: 'bg-[#EF4444]/15 text-[#EF4444] border-[#EF4444]/40',
      solidClasses: 'bg-[#EF4444] text-white',
    };
  }
  if (category.includes('esports') || category.includes('digital')) {
    return {
      label: 'Esports',
      classes: 'bg-[#7C3AED]/20 text-[#A78BFA] border-[#7C3AED]/45',
      solidClasses: 'bg-[#7C3AED] text-white',
    };
  }
  if (category.includes('combat') || category.includes('martial')) {
    return {
      label: 'Combat',
      classes: 'bg-orange-500/15 text-orange-400 border-orange-500/35',
      solidClasses: 'bg-orange-500 text-slate-950',
    };
  }
  if (category.includes('strategy') || category.includes('mind') || category.includes('board')) {
    return {
      label: 'Strategy',
      classes: 'bg-sky-500/15 text-sky-400 border-sky-500/35',
      solidClasses: 'bg-sky-500 text-slate-950',
    };
  }
  if (category.includes('indigenous') || category.includes('traditional')) {
    return {
      label: 'Heritage',
      classes: 'bg-amber-500/15 text-amber-400 border-amber-500/35',
      solidClasses: 'bg-amber-500 text-slate-950',
    };
  }
  return {
    label: article?.category ? shortenCategory(article.category) : 'Feature',
    classes: 'bg-[#10B981]/15 text-[#10B981] border-[#10B981]/35',
    solidClasses: 'bg-[#10B981] text-[#0B0E14]',
  };
}

export function shortenCategory(category) {
  if (!category) return 'All';
  const map = {
    'Esports & Competitive Digital Gaming': 'Esports',
    'Field & Team Ball Sports': 'Team Sports',
    'Combat Sports & Martial Arts': 'Combat',
    'Board, Tile & Strategy Games': 'Board & Strategy',
    'Indigenous, Folk & Traditional Games': 'Traditional',
    'Racquet & Paddle Sports': 'Racquet',
    'Target & Precision Sports': 'Precision',
    'Mind Sports & Tabletop Games': 'Mind & Tabletop',
    'Winter & Ice Sports': 'Winter & Ice',
    'Water & Aquatic Sports': 'Aquatic',
    'Extreme & Adventure Sports': 'Extreme',
    'Athletic & Gymnastic Disciplines': 'Athletics',
  };
  return map[category] || category.split('&')[0].trim();
}
