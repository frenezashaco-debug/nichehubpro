/* ================================================================
   NicheHubPro — Main JS
   ================================================================ */

document.addEventListener('DOMContentLoaded', function () {

  // ── READING PROGRESS BAR ──────────────────────────────────────
  var bar = document.getElementById('progress-bar');
  if (bar) {
    window.addEventListener('scroll', function () {
      var scrollTop = window.scrollY || document.documentElement.scrollTop;
      var docHeight = document.documentElement.scrollHeight - window.innerHeight;
      var pct = docHeight > 0 ? Math.min((scrollTop / docHeight) * 100, 100) : 0;
      bar.style.width = pct + '%';
    }, { passive: true });
  }

  // ── MOBILE NAV BURGER ─────────────────────────────────────────
  var burger = document.getElementById('burger');
  var mobileNav = document.getElementById('nav-mobile');
  if (burger && mobileNav) {
    burger.addEventListener('click', function () {
      var isOpen = mobileNav.classList.toggle('open');
      burger.setAttribute('aria-expanded', isOpen);
    });
    // Close on outside click
    document.addEventListener('click', function (e) {
      if (!burger.contains(e.target) && !mobileNav.contains(e.target)) {
        mobileNav.classList.remove('open');
      }
    });
  }

  // ── BACK TO TOP ───────────────────────────────────────────────
  var btt = document.getElementById('back-to-top');
  if (btt) {
    window.addEventListener('scroll', function () {
      btt.classList.toggle('visible', window.scrollY > 400);
    }, { passive: true });
    btt.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // ── FAQ ACCORDION ─────────────────────────────────────────────
  document.querySelectorAll('.faq-q').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var item = this.closest('.faq-item');
      var isOpen = item.classList.contains('open');
      // Close all
      document.querySelectorAll('.faq-item').forEach(function (el) {
        el.classList.remove('open');
      });
      // Open clicked if it was closed
      if (!isOpen) item.classList.add('open');
    });
  });

  // ── READING TIME (article pages) ─────────────────────────────
  var articleBody = document.getElementById('article-body');
  var readTimeEl = document.getElementById('read-time');
  if (articleBody && readTimeEl) {
    var words = articleBody.innerText.trim().split(/\s+/).length;
    var minutes = Math.max(1, Math.round(words / 220));
    readTimeEl.textContent = minutes;
  }

  // ── CATEGORY TABS (filter) ────────────────────────────────────
  document.querySelectorAll('.cat-tab').forEach(function (tab) {
    tab.addEventListener('click', function () {
      document.querySelectorAll('.cat-tab').forEach(function (t) {
        t.classList.remove('active');
      });
      this.classList.add('active');
      // In a real implementation this would filter cards
      // For now just visual activation
    });
  });

  // ── SMOOTH ANCHOR SCROLL ─────────────────────────────────────
  document.querySelectorAll('a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        var offset = 80;
        var top = target.getBoundingClientRect().top + window.scrollY - offset;
        window.scrollTo({ top: top, behavior: 'smooth' });
      }
    });
  });

  // ── STICKY NAV SHADOW ON SCROLL ───────────────────────────────
  var nav = document.querySelector('.nav');
  if (nav) {
    window.addEventListener('scroll', function () {
      nav.style.boxShadow = window.scrollY > 10
        ? '0 4px 20px rgba(0,0,0,0.08)'
        : '0 1px 3px rgba(0,0,0,0.07)';
    }, { passive: true });
  }

});
