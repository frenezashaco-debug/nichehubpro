/* Shared GA4 setup. Configure once to avoid duplicate automatic page views. */
(function () {
  'use strict';
  var id = 'G-PHY346X94N';
  if (!/^(www\.)?nichehubpro\.com$/.test(window.location.hostname)) return;
  if (window.nicheHubAnalyticsLoaded || window['ga-disable-' + id]) return;
  window.nicheHubAnalyticsLoaded = true;
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', id);
  var tag = document.createElement('script');
  tag.async = true;
  tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + id;
  document.head.appendChild(tag);
}());
