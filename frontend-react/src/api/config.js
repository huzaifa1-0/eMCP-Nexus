// In dev mode, use relative /api so Vite proxy handles CORS.
// In production (built), use the full backend URL from env.
export const API_BASE_URL =
  import.meta.env.DEV
    ? '/api'
    : (import.meta.env.VITE_API_BASE_URL || 'https://emcp-nexus-production.up.railway.app/api');

export async function fetchWithTimeout(url, options = {}, timeout = 8000) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  try {
    const response = await fetch(url, { ...options, signal: controller.signal });
    clearTimeout(id);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || errorData.message || `Server returned ${response.status}`);
    }
    return response;
  } catch (error) {
    clearTimeout(id);
    if (error.name === 'AbortError') throw new Error('Request timeout: Server is not responding');
    if (error.name === 'TypeError') throw new Error('Network error: Cannot connect to the server');
    throw error;
  }
}
