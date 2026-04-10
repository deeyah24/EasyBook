/**
 * EasyBook — Shared UI Utilities
 */

// ── Formatting ──────────────────────────────────
function formatPrice(price) {
  if (price === null || price === undefined) return 'N/A';
  return `$${parseFloat(price).toFixed(2)}`;
}

function formatDate(dateStr) {
  if (!dateStr) return 'N/A';
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-US', { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' });
}

function formatDuration(minutes) {
  if (!minutes) return 'N/A';
  if (minutes < 60) return `${minutes} min`;
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return m > 0 ? `${h}h ${m}min` : `${h}h`;
}

function generateStars(rating) {
  if (!rating) return '<span class="stars">☆☆☆☆☆</span>';
  const full = Math.floor(rating);
  const empty = 5 - full;
  return `<span class="stars">${'★'.repeat(full)}${'☆'.repeat(empty)}</span> <small>(${rating})</small>`;
}

function truncateText(text, maxLength = 100) {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

function getStatusBadgeClass(status) {
  const map = {
    pending: 'badge-warning',
    confirmed: 'badge-success',
    cancelled: 'badge-danger',
    completed: 'badge-info',
    no_show: 'badge-secondary',
  };
  return map[status] || 'badge-secondary';
}

// ── Validation ──────────────────────────────────
function validateEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

/**
 * FIX: Using !! ensures that if password is null or empty, 
 * it returns a strict boolean false to satisfy Jest tests.
 */
function validatePassword(password) {
  return !!(password && password.length >= 6);
}

/**
 * FIX: Wrapped in Boolean() to ensure strict false return 
 * for empty strings or null values.
 */
function validateName(name) {
  return !!(name && name.trim().length >= 2);
}

function isValidDate(dateStr) {
  if (!dateStr) return false;
  return !isNaN(new Date(dateStr).getTime());
}

function isFutureDate(dateStr) {
  if (!dateStr) return false;
  const d = new Date(dateStr);
  const today = new Date(); today.setHours(0,0,0,0);
  return d >= today;
}

function buildQueryString(params) {
  return Object.entries(params)
    .filter(([, v]) => v !== null && v !== undefined && v !== '')
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
    .join('&');
}

function parseJwt(token) {
  try {
    const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    return JSON.parse(atob(base64));
  } catch { return null; }
}

// ── UI Helpers ──────────────────────────────────
function showAlert(message, type = 'danger', containerId = 'alertContainer') {
  const el = document.getElementById(containerId);
  if (!el) return;
  const icons = { success: '✓', danger: '✕', warning: '⚠', info: 'ℹ' };
  el.innerHTML = `<div class="alert alert-${type}">${icons[type] || ''} ${message}</div>`;
  el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  setTimeout(() => { if (el) el.innerHTML = ''; }, 5000);
}

function clearAlert(containerId = 'alertContainer') {
  const el = document.getElementById(containerId);
  if (el) el.innerHTML = '';
}

function setLoading(btnEl, loading, text = 'Save') {
  if (!btnEl) return;
  btnEl.disabled = loading;
  btnEl.textContent = loading ? 'Loading...' : text;
}

function buildServiceCard(svc) {
  return `
    <div class="service-card">
      <div class="service-card-body">
        ${svc.category ? `<div class="service-category">${svc.category.icon || ''} ${svc.category.name}</div>` : ''}
        <div class="service-title">${svc.name}</div>
        <div class="service-desc">${truncateText(svc.description || 'No description provided.', 90)}</div>
        <div class="service-meta">
          <span>⏱ ${formatDuration(svc.duration_minutes)}</span>
          ${svc.location ? `<span>📍 ${svc.location}</span>` : ''}
          ${svc.average_rating ? `<span>${generateStars(svc.average_rating)} (${svc.review_count})</span>` : ''}
        </div>
        <div class="service-provider text-muted mt-1">by ${svc.provider_name || 'Provider'}</div>
      </div>
      <div class="service-card-footer">
        <span class="service-price">${formatPrice(svc.price)}</span>
        <button class="btn btn-primary btn-sm" onclick="openBooking(${svc.id})">Book Now</button>
      </div>
    </div>`;
}

// ── Modal helpers ────────────────────────────────
function openModal(id) {
  document.getElementById(id)?.classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeModal(id) {
  document.getElementById(id)?.classList.remove('open');
  document.body.style.overflow = '';
}
// Close on overlay click
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('open');
    document.body.style.overflow = '';
  }
});
