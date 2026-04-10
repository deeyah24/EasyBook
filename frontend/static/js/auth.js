/**
 * EasyBook — Auth Module
 * Shared login state, token management, and nav updates
 */

function getUser() {
  try { return JSON.parse(localStorage.getItem('eb_user') || 'null'); } catch { return null; }
}

function getToken() { return localStorage.getItem('eb_token'); }

function isLoggedIn() { return !!getToken(); }

function setSession(token, user) {
  localStorage.setItem('eb_token', token);
  localStorage.setItem('eb_user', JSON.stringify(user));
}

function clearSession() {
  localStorage.removeItem('eb_token');
  localStorage.removeItem('eb_user');
}

function logout() {
  clearSession();
  window.location.href = '/login.html';
}

function requireAuth() {
  if (!isLoggedIn()) {
    window.location.href = '/login.html?redirect=' + encodeURIComponent(window.location.href);
    return false;
  }
  return true;
}

function requireRole(role) {
  const user = getUser();
  if (!user || user.role !== role) {
    showAlert('Access denied.', 'danger');
    return false;
  }
  return true;
}

function initAuth() {
  const navbar = document.getElementById('navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      navbar.classList.toggle('scrolled', window.scrollY > 20);
    });
  }
  updateNavAuth();
}

function updateNavAuth() {
  const navAuth = document.getElementById('navAuth');
  const navUser = document.getElementById('navUser');
  if (!navAuth || !navUser) return;
  if (isLoggedIn()) {
    navAuth.style.display = 'none';
    navUser.style.display = 'flex';
    navUser.style.alignItems = 'center';
    navUser.style.gap = '1rem';
  } else {
    navAuth.style.display = 'flex';
    navAuth.style.alignItems = 'center';
    navAuth.style.gap = '0.5rem';
    navUser.style.display = 'none';
  }
}

function toggleNav() {
  document.getElementById('navLinks')?.classList.toggle('open');
}
