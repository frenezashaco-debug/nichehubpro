# Cloudflare redirect rules for NicheHubPro

The site is hosted on GitHub Pages, which cannot issue server-side redirects for
extensionless article URLs or legacy WordPress paths. Use Cloudflare Redirect
Rules, not JavaScript or meta-refresh redirect pages, for these cases.

## 1. Canonical article URL rule

Create a **Single Redirect** rule named `Canonical article URLs`.

- When the incoming request matches this expression:

  ```text
  http.request.uri.path matches "^/articles/[^/.]+$"
  ```

- Then use a **Dynamic** redirect with this target expression:

  ```text
  concat("https://nichehubpro.com", http.request.uri.path, ".html")
  ```

- Status code: **301 Permanent Redirect**
- Preserve query string: **On**

This consolidates `/articles/article-slug` into the canonical
`/articles/article-slug.html` URL. It must be placed before broad legacy rules.

## 2. Legacy URLs from Search Console

Export the GSC report for `Not found (404)` as CSV. For each URL:

- Use **301** only when a close, relevant replacement article exists.
- Use **410 Gone** when the old URL has no relevant replacement. Do not redirect
  unrelated pages to the homepage.
- Do not create redirects with HTML, JavaScript, or a meta refresh. They return
  HTTP 200 and do not reliably transfer ranking signals.

Keep the source URL, chosen target, and rationale in a mapping spreadsheet
before adding bulk redirects. After deployment, test a sample of each group
with the Cloudflare Redirect Rules test tool, then validate the fix in GSC.
