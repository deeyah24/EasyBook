/**
 * FRONTEND TESTS - EasyBook
 * Tests for frontend utility functions and UI logic using Jest
 */

// ─── Utility functions (mirrors what's in app.js) ───────────────────────────

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

function validateEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function validatePassword(password) {
  return password && password.length >= 6;
}

function validateName(name) {
  return name && name.trim().length >= 2;
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

function generateStars(rating) {
  if (!rating) return '☆☆☆☆☆';
  const full = Math.floor(rating);
  const empty = 5 - full;
  return '★'.repeat(full) + '☆'.repeat(empty);
}

function truncateText(text, maxLength = 100) {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

function isValidDate(dateStr) {
  if (!dateStr) return false;
  const d = new Date(dateStr);
  return !isNaN(d.getTime());
}

function isFutureDate(dateStr) {
  if (!dateStr) return false;
  const d = new Date(dateStr);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
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
  } catch {
    return null;
  }
}

// ─── Tests ───────────────────────────────────────────────────────────────────

// Mock atob for Node environment
global.atob = (str) => Buffer.from(str, 'base64').toString('binary');

describe('Frontend Utility: formatPrice', () => {
  test('formats a number as price with 2 decimals', () => {
    expect(formatPrice(50)).toBe('$50.00');
  });

  test('formats decimal price correctly', () => {
    expect(formatPrice(29.9)).toBe('$29.90');
  });

  test('returns N/A for null price', () => {
    expect(formatPrice(null)).toBe('N/A');
  });

  test('returns N/A for undefined price', () => {
    expect(formatPrice(undefined)).toBe('N/A');
  });

  test('handles zero price', () => {
    expect(formatPrice(0)).toBe('$0.00');
  });
});

describe('Frontend Utility: formatDuration', () => {
  test('formats minutes under 60 correctly', () => {
    expect(formatDuration(30)).toBe('30 min');
  });

  test('formats exactly 60 minutes as 1h', () => {
    expect(formatDuration(60)).toBe('1h');
  });

  test('formats 90 minutes as 1h 30min', () => {
    expect(formatDuration(90)).toBe('1h 30min');
  });

  test('formats 120 minutes as 2h', () => {
    expect(formatDuration(120)).toBe('2h');
  });

  test('returns N/A for null', () => {
    expect(formatDuration(null)).toBe('N/A');
  });
});

describe('Frontend Utility: validateEmail', () => {
  test('accepts valid email', () => {
    expect(validateEmail('user@example.com')).toBe(true);
  });

  test('accepts email with subdomain', () => {
    expect(validateEmail('user@mail.example.co.uk')).toBe(true);
  });

  test('rejects email without @', () => {
    expect(validateEmail('notanemail')).toBe(false);
  });

  test('rejects email without domain', () => {
    expect(validateEmail('user@')).toBe(false);
  });

  test('rejects empty string', () => {
    expect(validateEmail('')).toBe(false);
  });
});

describe('Frontend Utility: validatePassword', () => {
  test('accepts password with 6+ chars', () => {
    expect(validatePassword('secure123')).toBe(true);
  });

  test('rejects password shorter than 6 chars', () => {
    expect(validatePassword('abc')).toBe(false);
  });

  test('rejects empty password', () => {
    expect(validatePassword('')).toBe(false);
  });

  test('rejects null', () => {
    expect(validatePassword(null)).toBe(false);
  });
});

describe('Frontend Utility: validateName', () => {
  test('accepts name with 2+ chars', () => {
    expect(validateName('Jo')).toBe(true);
  });

  test('rejects single character name', () => {
    expect(validateName('J')).toBe(false);
  });

  test('rejects empty name', () => {
    expect(validateName('')).toBe(false);
  });

  test('rejects whitespace-only name', () => {
    expect(validateName('   ')).toBe(false);
  });
});

describe('Frontend Utility: getStatusBadgeClass', () => {
  test('pending maps to badge-warning', () => {
    expect(getStatusBadgeClass('pending')).toBe('badge-warning');
  });

  test('confirmed maps to badge-success', () => {
    expect(getStatusBadgeClass('confirmed')).toBe('badge-success');
  });

  test('cancelled maps to badge-danger', () => {
    expect(getStatusBadgeClass('cancelled')).toBe('badge-danger');
  });

  test('completed maps to badge-info', () => {
    expect(getStatusBadgeClass('completed')).toBe('badge-info');
  });

  test('unknown status maps to badge-secondary', () => {
    expect(getStatusBadgeClass('unknown')).toBe('badge-secondary');
  });
});

describe('Frontend Utility: generateStars', () => {
  test('generates 5 stars for rating 5', () => {
    expect(generateStars(5)).toBe('★★★★★');
  });

  test('generates 3 filled and 2 empty for rating 3', () => {
    expect(generateStars(3)).toBe('★★★☆☆');
  });

  test('generates all empty for no rating', () => {
    expect(generateStars(null)).toBe('☆☆☆☆☆');
  });

  test('generates 1 star for rating 1', () => {
    expect(generateStars(1)).toBe('★☆☆☆☆');
  });
});

describe('Frontend Utility: truncateText', () => {
  test('returns text unchanged if under limit', () => {
    expect(truncateText('Hello world', 100)).toBe('Hello world');
  });

  test('truncates long text with ellipsis', () => {
    const long = 'a'.repeat(110);
    const result = truncateText(long, 100);
    expect(result.endsWith('...')).toBe(true);
    expect(result.length).toBe(103);
  });

  test('returns empty string for null', () => {
    expect(truncateText(null)).toBe('');
  });
});

describe('Frontend Utility: isValidDate', () => {
  test('accepts valid date string', () => {
    expect(isValidDate('2025-06-15')).toBe(true);
  });

  test('rejects invalid date string', () => {
    expect(isValidDate('not-a-date')).toBe(false);
  });

  test('rejects empty string', () => {
    expect(isValidDate('')).toBe(false);
  });
});

describe('Frontend Utility: buildQueryString', () => {
  test('builds correct query string from object', () => {
    const result = buildQueryString({ page: 1, per_page: 10 });
    expect(result).toContain('page=1');
    expect(result).toContain('per_page=10');
  });

  test('filters out null and empty values', () => {
    const result = buildQueryString({ a: 'hello', b: null, c: '' });
    expect(result).toBe('a=hello');
  });

  test('returns empty string for empty object', () => {
    expect(buildQueryString({})).toBe('');
  });
});

describe('Frontend Utility: parseJwt', () => {
  test('parses valid JWT payload', () => {
    // Create a fake JWT: header.payload.signature
    const payload = { sub: '42', role: 'customer' };
    const encoded = Buffer.from(JSON.stringify(payload)).toString('base64');
    const fakeJwt = `header.${encoded}.signature`;
    const result = parseJwt(fakeJwt);
    expect(result).toBeTruthy();
    expect(result.sub).toBe('42');
  });

  test('returns null for invalid JWT', () => {
    expect(parseJwt('not.a.jwt.at.all.broken')).toBeNull();
  });
});
