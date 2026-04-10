/**
 * EasyBook — API Client
 * Centralized fetch wrapper for all backend calls
 */

// Use relative URL so requests go through Nginx proxy (works in Docker and locally)
const API_BASE = window.API_BASE || '/api';

const api = {
  _getHeaders(auth = true) {
    const headers = { 'Content-Type': 'application/json' };
    if (auth) {
      const token = localStorage.getItem('eb_token');
      if (token) headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  },

  async _request(method, path, body = null, auth = true) {
    const url = `${API_BASE}${path}`;
    const opts = { method, headers: this._getHeaders(auth) };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(url, opts);
    let data;
    try { data = await res.json(); } catch { data = {}; }
    if (!res.ok) throw { status: res.status, message: data.error || data.message || 'Request failed', data };
    return data;
  },

  get:    (path, auth = true)       => api._request('GET', path, null, auth),
  post:   (path, body, auth = true)  => api._request('POST', path, body, auth),
  put:    (path, body, auth = true)  => api._request('PUT', path, body, auth),
  delete: (path, auth = true)        => api._request('DELETE', path, null, auth),
};
