# Priority discovery batch, September 22, 2026

## Scope

Improve five priority pages from the 22-URL Discovered, currently not indexed export. This is not a diagnosis of Google's crawl scheduling and does not guarantee indexing or AdSense approval.

## Changes

- Reworked the Android application comparison using official product documentation. Removed unverified personal credentials, user-retention claims, an unsupported proprietary-app recommendation, and inaccurate Notion offline guidance. The article explicitly discloses that it is not a hands-on benchmark.
- Reworked workplace overthinking guidance. Removed unsupported percentages, neurological mechanisms, fixed recovery timelines, and a fictional testimonial presented as a quote. Added inline NHS, NIMH, and WHO references, workplace-context limitations, and guidance on professional support.
- Added navigation guidance and institutional references to Anxiety and Stress, Sleep and Energy, and Overthinking hubs.
- Added contextual links in seven related articles. Their remaining content was not comprehensively rewritten or medically reviewed in this batch.
- Updated the two article descriptions in HTML, structured data, and the article API. Preserved publication dates and canonical URLs. Updated sitemap lastmod only for the five substantially revised pages.
- Kept the scheduled article publisher paused. Updated FAQ accessibility state in the shared handler and the Android article's inline handler.

## Local verification

Run `node scripts/check_discovered_priority.mjs` from the repository root. It checks sitemap membership, canonical URLs, local link destinations, article descriptions, JSON-LD, source sections, five FAQs per rewritten article, and FAQ opening/closing state transitions.

Distinct referring pages among the 161 sitemap URLs, including navigation and related links:

| Destination | Before | After |
| --- | ---: | ---: |
| Android app comparison | 1 | 3 |
| Anxiety and Stress | 2 | 6 |
| Sleep and Energy | 2 | 6 |
| Overthinking at work | 3 | 6 |
| Overthinking hub | 4 | 9 |

These counts measure link presence, not contextual quality, authority, or Google's discovery of those links.

## Remaining external checks

After deployment, verify the five live pages, then run URL Inspection in the owner's Search Console account. Request indexing once for eligible priority pages. Keep the export as a baseline and compare later reports rather than repeatedly submitting the same requests.

The current export contains placeholder last-crawled dates of 1970-01-01. Do not interpret them as actual Googlebot visits.
