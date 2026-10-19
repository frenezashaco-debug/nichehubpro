/* Optional analytics and article AdSense bootstrap. Ad consent is handled by Google's CMP. */
(function () {
  'use strict';
  var id = 'G-PHY346X94N';
  if (!/^(www\.)?nichehubpro\.com$/.test(window.location.hostname)) return;
  if (window.nicheHubConsentInitialized) return;
  window.nicheHubConsentInitialized = true;
  var key = 'nhp-analytics-choice-v1';
  var externalOptOut = window['ga-disable-' + id] === true;
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  window.gtag('consent', 'default', {
    analytics_storage: 'denied', ad_storage: 'denied',
    ad_user_data: 'denied', ad_personalization: 'denied'
  });
  // Existing articles and publisher_v2.py share this file. Load Google's
  // published CMP through the AdSense tag, never grant ad consent here.
  // Keep this independent of the optional Analytics choice.
  if (/^\/articles\/[^/]+\.html$/.test(window.location.pathname)) {
    function loadArticleAdsense() {
      if (document.querySelector('script[src*="pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"]')) return;
      var ads = document.createElement('script');
      ads.async = true;
      ads.crossOrigin = 'anonymous';
      ads.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7481817319849340';
      document.head.appendChild(ads);
    }
    if (document.readyState === 'complete') loadArticleAdsense();
    else window.addEventListener('load', loadArticleAdsense, { once: true });
  }
  function apply(allowed) {
    allowed = allowed && !externalOptOut;
    window['ga-disable-' + id] = !allowed;
    window.gtag('consent', 'update', { analytics_storage: allowed ? 'granted' : 'denied' });
    if (!allowed || window.nicheHubAnalyticsLoaded) return;
    window.nicheHubAnalyticsLoaded = true;
    window.gtag('js', new Date());
    window.gtag('config', id);
    var tag = document.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + id;
    document.head.appendChild(tag);
  }
  var choice = null;
  try { choice = window.localStorage.getItem(key); } catch (_) {}
  apply(choice === 'granted');
  function mount() {
    var panel = document.createElement('section');
    panel.setAttribute('aria-label', 'Analytics privacy choices');
    panel.style.cssText = 'position:fixed;bottom:52px;left:16px;right:16px;max-width:560px;padding:20px;background:#fff;color:#142035;border:1px solid #b7c2ce;border-radius:12px;box-shadow:0 4px 24px #0002;z-index:10000;font:16px/1.5 system-ui';
    var text = document.createElement('p');
    text.textContent = 'May we use optional Google Analytics to understand which pages visitors use? You can decline and still use the entire site. Change your choice anytime using Privacy choices.';
    panel.appendChild(text);
    function button(label, action, parent) {
      var b = document.createElement('button');
      b.type = 'button'; b.textContent = label;
      b.style.cssText = 'padding:10px 14px;margin:4px;border:1px solid #45556b;border-radius:6px;background:white;color:#142035;cursor:pointer;font:inherit';
      b.addEventListener('click', action); parent.appendChild(b); return b;
    }
    function choose(value) {
      choice = value;
      try { window.localStorage.setItem(key, value); } catch (_) {}
      apply(value === 'granted'); panel.hidden = true; settings.focus();
    }
    button('Allow analytics', function () { choose('granted'); }, panel);
    button('Decline analytics', function () { choose('denied'); }, panel);
    var link = document.createElement('a');
    link.href = '/privacy/'; link.textContent = 'Privacy policy';
    panel.appendChild(link);
    document.body.appendChild(panel);
    panel.hidden = choice === 'granted' || choice === 'denied' || externalOptOut;
    var settings = button('Privacy choices', function () { panel.hidden = false; }, document.body);
    settings.style.cssText += ';position:fixed;bottom:8px;left:12px;z-index:9999;font-size:13px';
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
}());
