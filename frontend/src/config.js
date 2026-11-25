/**
 * WorldGames AI - Frontend API Configuration.
 * Uses VITE_API_BASE_URL when provided, defaulting to the Render backend URL.
 */
const rawApiBase = import.meta.env.VITE_API_BASE_URL || 'https://world-games-lhi1.onrender.com';

export const API_BASE = rawApiBase.replace(/\/+$/, '');

export function apiUrl(path) {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE}${cleanPath}`;
}
