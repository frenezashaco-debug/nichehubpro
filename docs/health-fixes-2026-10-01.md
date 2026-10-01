# Health fixes, October 1, 2026

- Added a shared GA4 loader to all 163 sitemap pages and the publisher template. It configures the existing property once, honors the existing GA disable flag, and skips non-production hosts. No additional manual page_view event is sent. Account receipt still requires GA4 Realtime/DebugView confirmation.
- Replaced 40 noncanonical internal-link occurrences across 14 articles with existing `/articles/*.html` destinations. Nine of the old URLs returned 404; the other unique destinations redirected successfully.
- Enabled Cloudflare Always Use HTTPS. Live checks returned 301 for the HTTP homepage and an article URL, preserving its query string.
- Added six contextual links from relevant articles to the app-workflow, attention-span, and mental-clutter guides. All three now have at least two distinct static referring pages.
- Rewrote the anxiety-attacks article based on the anxiety-attack queries visible in the owner's Search Console screenshot. Removed unsupported percentages, guaranteed response times, and claims that chest symptoms cannot be dangerous. Added direct NIMH/NHS sources, an explicitly illustrative example, five accessible FAQs, and clear care guidance. Synchronized metadata and API copy, preserving publication date and updating modification date.

The screenshot provides aggregate performance and sample queries, not page-level opportunity rankings. Search Console in the accessible browser requires sign-in. Further selection needs the Pages and Queries exports; no ranking or traffic improvement is claimed.

Validation:

```
python scripts/check_health_fixes.py
node scripts/check_analytics.cjs
git diff --check
```

The article's FAQ was also opened in a browser and its expanded answer verified. Analytics configuration was checked for duplicate initialization and opt-out behavior. This is not a full medical review of the remaining articles or proof of Google indexing.
