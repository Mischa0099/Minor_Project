import axios from 'axios';

const api = axios.create({
  // In development prefer a relative URL so CRA dev server proxy (package.json proxy)
  // forwards to the backend. Set REACT_APP_API_URL to override (e.g. production).
  baseURL: process.env.REACT_APP_API_URL ?? '',
  timeout: 30000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Log and normalize errors to make frontend error handling easier
api.interceptors.response.use(
  (res) => res,
  (err) => {
    // Log for debugging
    console.error('API error:', err.response?.status, err.response?.data || err.message);
    // Normalize error body to a user-friendly string. Some backends return
    // { message: '...', msg: '...' } or other shapes; avoid attaching raw
    // objects which React might try to render.
    let normalized = '';
    const data = err.response?.data;
    if (!data) normalized = err.message || 'Network error';
    else if (typeof data === 'string') normalized = data;
    else if (typeof data === 'object') {
      normalized = data.message || data.msg || data.error || JSON.stringify(data);
    } else normalized = String(data);

    return Promise.reject(Object.assign(err, { friendlyMessage: normalized }));
  }
);

export default api;
