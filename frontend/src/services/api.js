/**
 * World Games - Dedicated API Client
 * Connects cleanly to the FastAPI backend via VITE_API_URL (or Vite /api proxy in local dev).
 */

const rawBase =
  import.meta.env.VITE_API_URL ||
  import.meta.env.VITE_API_BASE_URL ||
  '';

export const API_BASE = rawBase.replace(/\/+$/, '');

export function apiUrl(path) {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE}${cleanPath}`;
}

async function requestJson(path, options = {}) {
  const response = await fetch(apiUrl(path), {
    headers: {
      Accept: 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const errData = await response.json();
      if (errData?.detail) detail = errData.detail;
    } catch {
      // Ignore JSON parse failure on error body
    }
    throw new Error(detail);
  }

  return response.json();
}

/**
 * Fetches published articles/playbooks/news with optional combinatorial filters.
 */
export async function fetchFeed({
  category,
  region,
  articleType,
  search,
  date,
  limit = 30,
  offset = 0,
} = {}) {
  const params = new URLSearchParams();
  if (category && category !== 'All') params.set('category', category);
  if (region && region !== 'All') params.set('region', region);
  if (articleType && articleType !== 'All') params.set('article_type', articleType);
  if (search && search.trim()) params.set('search', search.trim());
  if (date) params.set('date', date);
  params.set('limit', String(limit));
  params.set('offset', String(offset));

  return requestJson(`/api/v1/publish/feed?${params.toString()}`, { cache: 'no-store' });
}

/**
 * Fetches a single full article by slug.
 */
export async function fetchArticleBySlug(slug) {
  return requestJson(`/api/v1/articles/slug/${encodeURIComponent(slug)}`);
}

/**
 * Fetches a single full article by ID.
 */
export async function fetchArticleById(id) {
  return requestJson(`/api/v1/articles/id/${encodeURIComponent(id)}`);
}

/**
 * Fetches global taxonomy (categories & regions) from backend.
 */
export async function fetchTaxonomy() {
  return requestJson('/api/v1/topics/taxonomy');
}

/**
 * Fetches real-time platform stats without browser cache conditional 304s.
 */
export async function fetchSystemStats() {
  return requestJson('/api/v1/publish/stats', { cache: 'no-store' });
}
