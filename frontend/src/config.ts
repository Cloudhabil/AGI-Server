// In Docker (production): use empty string for relative URLs (nginx proxies /api/* to backend)
// In development: use localhost:8000
export const API_BASE = import.meta.env.VITE_API_URL ??
  (import.meta.env.PROD ? '' : 'http://localhost:8000');
export const API_TOKEN = import.meta.env.VITE_API_TOKEN || '';
export const API_USER_ROLE = (import.meta.env.VITE_USER_ROLE || 'admin').toLowerCase();
