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

  // ── SEARCH ────────────────────────────────────────────────────
  var navInner = document.querySelector('.nav-inner');
  if (navInner) {
    // Inject search button before burger
    var searchBtn = document.createElement('button');
    searchBtn.className = 'nav-search-btn';
    searchBtn.setAttribute('aria-label', 'Search articles');
    searchBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>';
    var burger = navInner.querySelector('.nav-burger');
    navInner.insertBefore(searchBtn, burger || null);

    // Build overlay
    var overlay = document.createElement('div');
    overlay.className = 'search-overlay';
    overlay.innerHTML =
      '<div class="search-box">' +
        '<input type="text" class="search-input" placeholder="Search articles..." autocomplete="off" spellcheck="false">' +
        '<div class="search-results"><div class="search-hint">Start typing to find articles&hellip;</div></div>' +
      '</div>';
    document.body.appendChild(overlay);

    var sInput   = overlay.querySelector('.search-input');
    var sResults = overlay.querySelector('.search-results');

    function catClass(cat) {
      if (!cat) return '';
      var c = cat.toLowerCase();
      if (c.includes('mental'))     return 'mw';
      if (c.includes('product'))    return 'pr';
      if (c.includes('lifestyle'))  return 'hl';
      return '';
    }

    function doSearch(q) {
      var articles = (typeof ARTICLES !== 'undefined') ? ARTICLES : [];
      if (!q.trim()) {
        sResults.innerHTML = '<div class="search-hint">Start typing to find articles&hellip;</div>';
        return;
      }
      var lq = q.toLowerCase();
      var hits = articles.filter(function(a) {
        return (a.title  && a.title.toLowerCase().includes(lq))  ||
               (a.excerpt && a.excerpt.toLowerCase().includes(lq)) ||
               (a.category && a.category.toLowerCase().includes(lq));
      }).slice(0, 8);

      if (!hits.length) {
        sResults.innerHTML = '<div class="search-no-results">No results for &ldquo;' + q + '&rdquo;</div>';
        return;
      }
      sResults.innerHTML = hits.map(function(a) {
        var root = (window.location.pathname.startsWith('/articles/')) ? '../' : '/';
        return '<a class="search-result-item" href="' + root + 'articles/' + a.slug + '.html">' +
          '<div>' +
            '<div class="search-result-cat ' + catClass(a.category) + '">' + (a.category || '') + '</div>' +
            '<div class="search-result-title">' + a.title + '</div>' +
          '</div>' +
        '</a>';
      }).join('');
    }

    function openSearch() {
      overlay.classList.add('open');
      sInput.value = '';
      sResults.innerHTML = '<div class="search-hint">Start typing to find articles&hellip;</div>';
      setTimeout(function() { sInput.focus(); }, 50);
    }
    function closeSearch() { overlay.classList.remove('open'); }

    searchBtn.addEventListener('click', openSearch);
    overlay.addEventListener('click', function(e) { if (e.target === overlay) closeSearch(); });
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') closeSearch();
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') { e.preventDefault(); openSearch(); }
    });
    sInput.addEventListener('input', function() { doSearch(this.value); });
  }

});
