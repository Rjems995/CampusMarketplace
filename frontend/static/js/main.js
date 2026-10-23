/**
 * static/js/main.js — Campus Marketplace
 * Global JS: dark mode, toast auto-dismiss, favorite cards,
 * notification polling, SocketIO user room.
 */

/* ── Dark / Light mode toggle ────────────────────────────── */
(function () {
  const html      = document.documentElement;
  const toggleBtn = document.getElementById('themeToggle');
  const icon      = document.getElementById('themeIcon');

  let saved = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  try { saved = localStorage.getItem('cm-theme') || saved; } catch (_) { /* Storage can be unavailable. */ }
  applyTheme(saved);

  toggleBtn?.addEventListener('click', () => {
    const next = html.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    try { localStorage.setItem('cm-theme', next); } catch (_) { /* Theme still works for this page. */ }
  });

  function applyTheme(theme) {
    theme = theme === 'dark' ? 'dark' : 'light';
    html.setAttribute('data-bs-theme', theme);
    toggleBtn?.setAttribute('aria-label', theme === 'dark' ? 'Use light theme' : 'Use dark theme');
    if (icon) {
      icon.className = theme === 'dark' ? 'bi bi-sun-fill fs-5' : 'bi bi-moon-stars fs-5';
    }
  }
})();


/* ── Auto-dismiss flash toasts ───────────────────────────── */
document.querySelectorAll('.toast.show').forEach(el => {
  setTimeout(() => {
    const toast = bootstrap.Toast.getOrCreateInstance(el);
    toast.hide();
  }, 4500);
});


/* ── Product card favorite buttons ───────────────────────── */
document.querySelectorAll('.fav-btn').forEach(btn => {
  btn.addEventListener('click', async function (e) {
    e.preventDefault();
    e.stopPropagation();

    const pid = this.dataset.productId;
    if (!pid) return;

    if (this.disabled) return;
    this.disabled = true;
    this.setAttribute('aria-busy', 'true');
    try {
      const res = await fetch(`/marketplace/listing/${pid}/favorite`, {
        method : 'POST',
        headers: { 'X-CSRFToken': getCsrfToken() },
      });
      if (res.redirected || res.status === 401) {
        window.location.href = '/auth/login';
        return;
      }
      if (!res.ok) throw new Error('Could not save listing');
      const data = await res.json();
      this.setAttribute('aria-pressed', String(data.favorited));
      this.setAttribute('aria-label', data.favorited ? 'Remove saved listing' : 'Save listing');
      this.title = data.favorited ? 'Remove saved listing' : 'Save listing';
      const iconEl = this.querySelector('i');
      if (iconEl) {
        iconEl.className = data.favorited
          ? 'bi bi-heart-fill text-danger'
          : 'bi bi-heart';
      }
    } catch (err) {
      showToast('Unable to update saved items', 'Please try again. Your connection or session may have expired.', 'danger');
    } finally {
      this.disabled = false;
      this.removeAttribute('aria-busy');
    }
  });
});


/* ── SocketIO — join personal room + notification badge ──── */
(function () {
  if (typeof io === 'undefined') return;     // SocketIO not loaded
  if (!document.body.dataset.userId) return; // not logged in

  const socket     = io();
  const userId     = document.body.dataset.userId;
  let notifBadge = document.getElementById('notifBadge');
  const msgBadge   = document.getElementById('msgBadge');

  socket.on('connect', () => {
    // Server join_room is handled via on_connect in routes/chat.py
  });

  socket.on('new_notification', (note) => {
    // Increment badge
    if (notifBadge) {
      const current = parseInt(notifBadge.textContent, 10) || 0;
      notifBadge.textContent = current + 1;
      notifBadge.classList.remove('d-none');
    } else {
      // Badge didn't exist yet — create it
      const bellLink = document.querySelector('[data-bs-target="#notifDropdown"], [title="Notifications"]');
      if (bellLink) {
        const span = document.createElement('span');
        span.id        = 'notifBadge';
        span.className = 'badge bg-danger rounded-pill position-absolute top-0 start-100 translate-middle';
        span.textContent = '1';
        bellLink.style.position = 'relative';
        bellLink.appendChild(span);
        notifBadge = span;
      }
    }

    // Show a small toast
    showToast(note.title, note.body || '', 'info');
  });
})();


/* ── Simple toast helper ─────────────────────────────────── */
function showToast(title, body, type = 'primary') {
  const container = document.querySelector('.flash-container') || createToastContainer();
  const id   = `toast-${Date.now()}`;
  const html = `
    <div id="${id}" class="toast show align-items-center text-bg-${type} border-0 mb-2" role="alert">
      <div class="d-flex">
        <div class="toast-body">
          <strong>${escapeHtml(title)}</strong>
          ${body ? '<br><span class="opacity-75">' + escapeHtml(body) + '</span>' : ''}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Dismiss notification"></button>
      </div>
    </div>`;
  container.insertAdjacentHTML('beforeend', html);
  const el    = document.getElementById(id);
  const toast = bootstrap.Toast.getOrCreateInstance(el);
  toast.show();
  setTimeout(() => toast.hide(), 5000);
}

function createToastContainer() {
  const div = document.createElement('div');
  div.className = 'flash-container position-fixed top-0 end-0 p-3';
  div.style.cssText = 'z-index:9999;margin-top:70px;';
  document.body.appendChild(div);
  return div;
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g,'&amp;')
    .replace(/</g,'&lt;')
    .replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;');
}


/* ── CSRF token helper ───────────────────────────────────── */
function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  if (meta) return meta.content;
  // Flask-WTF injects it into every form; grab from DOM
  const input = document.querySelector('input[name="csrf_token"]');
  return input ? input.value : '';
}


/* ── Confirm before dangerous form submits ───────────────── */
document.querySelectorAll('[data-confirm]').forEach(el => {
  el.addEventListener('click', function (e) {
    if (!confirm(this.dataset.confirm)) e.preventDefault();
  });
});


/* ── Back-to-top button (optional) ──────────────────────── */
window.addEventListener('scroll', () => {
  const btn = document.getElementById('backToTop');
  if (btn) btn.classList.toggle('d-none', window.scrollY < 400);
});
document.getElementById('backToTop')?.addEventListener('click', () =>
  window.scrollTo({ top: 0, behavior: 'smooth' })
);
