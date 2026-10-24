# Search priorities, 24 October 2026

## Evidence and reporting periods

Read directly from the authenticated Search Console property https://nichehubpro.com/.
Performance period shown: 22 July to 21 October 2026, last update about 4.5 hours before inspection.
Totals shown: 11 clicks, approximately 4.2K impressions, 0.3% CTR, average position 59.4.
These are rounded interface values. The indexing overview separately displays last update 16 October, so its counts are not a live crawl of today's site.

The supplied CSV export covers 16 July to 15 October, with 10 clicks and 4,407 impressions in Chart.csv. It is a different window and must not be treated as a before/after experiment. Pages.csv and Queries.csv are separate aggregations, not a query-to-page join.

## Public technical checks completed

The live sitemap contains 171 unique URLs. All 171 returned HTTP 200, stayed at the submitted URL, declared exactly that URL as canonical, and had no detected HTML robots or Googlebot noindex directive or X-Robots-Tag noindex header. No duplicate sitemap URL was found.

This verifies delivery and the checked indexing signals, not Google indexing, content quality, rankings, or ad approval. It does not test Googlebot rendering or every link on the site.

Evidence: reports/search-readiness-latest.json. Reproduce with scripts/audit_search_readiness.py.

Public ads.txt, robots.txt and sitemap.xml returned 200. The local ads.txt publisher ID is pub-7481817319849340. The extensionless /articles/natural-energy-boosters returns 301 to its canonical HTML URL.

## Traffic priorities

| Page | Impressions | Clicks | Average position | Next action |
| --- | ---: | ---: | ---: | --- |
| /articles/pomodoro-technique-explained-for-beginners.html | 102 | 0 | 10.6 | Preserve the 18 October revision. Measure an equal post-change window after recrawl; inspect queries with this page selected. |
| /articles/best-productivity-apps-in-2026.html | 124 | 0 | 15.8 | Review page-filtered queries, match comparison criteria to reader tasks, verify current official product facts before any factual update. |
| /articles/best-self-improvement-systems-explained.html | 57 | 2 | 21.1 | Preserve the revised content; inspect the queries driving its actual clicks and strengthen relevant incoming links only where useful. |
| /articles/how-to-recover-focus-after-a-distraction.html | 93 | 1 | 24.9 | Preserve its recent revision and use it as a relevant bridge to the Pomodoro guide. |
| /articles/natural-energy-boosters.html | 989 | 0 | 82.9 | Longer-term content/intent review. High impressions alone do not make this the quickest traffic opportunity. |
| /articles/best-foods-for-focus-and-concentration.html | 411 | 0 | 72.9 | Review search intent and evidence before rewriting health-related claims. |

Positions and CTR are averages over the displayed period, not fixed rankings. No traffic uplift is assumed.

## Indexing priorities

The overview shows 133 indexed, 566 not indexed, including 325 not found and 106 crawled/currently not indexed.

The first visible crawled/not-indexed examples include:

- /articles/how-to-relax-your-mind.html
- /articles/healthy-lifestyle-tips.html
- /articles/simple-morning-habits.html
- /articles/how-to-recover-from-emotional-burnout.html
- /articles/morning-routine-for-mental-health.html
- /articles/how-to-stay-calm-under-pressure.html
- /articles/healthy-living-tips.html
- /articles/improve-daily-routine.html
- /articles/success-habits.html
- /articles/healthy-daily-habits.html

Review distinct search intent and useful original material first, especially the similarly named lifestyle and daily-habit pages. These titles suggest a possible overlap to investigate, not proof of duplication. Use URL Inspection to check the individual current indexing state before requesting any recrawl.

## Legacy 404 sample

All ten visible examples were tested and still return 404:

- /best-productivity-apps-for-students/
- /benefits-of-green-tea-and-when-to-drink-it/
- /how-to-stop-comparing-yourself-to-others/
- /signs-you-need-a-mental-health-day/
- /decision-fatigue-and-how-to-overcome-it/
- /how-to-set-smart-goals-and-achieve-them/
- /benefits-of-strength-training-for-women/
- /what-to-eat-before-and-after-a-workout/
- /how-to-stop-negative-thoughts-at-night/
- /feed/

No equivalent current article was identified in the inspected inventory for these nine article URLs. Their slugs were absent from the inspected article/hub HTML and registry/sitemap references. Keep these statuses unless a genuine replacement or valuable incoming link establishes a reason to restore or redirect a specific page. Do not map them all to unrelated categories or the homepage.

Google guidance: https://support.google.com/webmasters/answer/2445990?hl=en and https://support.google.com/webmasters/answer/7440203?hl=en.

## Next implementation batch

1. Inspect page-filtered queries and URL Inspection for the three near-ranking traffic priorities.
2. Audit the overlapping lifestyle/habit pages for distinct reader value, then improve or consolidate only after mapping their content and incoming links.
3. Request recrawling only for materially changed priority pages whose current indexing state warrants it.
4. Recheck AdSense account status, live consent behavior and ads.txt recognition before submitting a new review. These account checks were not performed in this search audit.

No site article, Cloudflare redirect, Make scenario, AdSense submission or Search Console validation was changed during this audit.

## Follow-up implementation on 24 October

Individual URL Inspection shows all three traffic priorities as indexed: Pomodoro, best-productivity-apps-in-2026, and best-self-improvement-systems-explained. The healthy-lifestyle-tips URL also shows indexed despite its presence in the older crawled/not-indexed table. The individual inspection supersedes that stale example for this URL.

Exact page-filtered queries were read. Pomodoro: "pomodoro technique explained" (93 impressions), "pomodoro technique explanation" (1), "pomodoro work method" (1). Apps: "common daily frustrations that need an app 2026" (7), "best task apps for earning in 2026 in united states" (5), "best productivity apps 2026" (5), "best productivity apps in 2026" (2), plus lower-volume queries. Self-improvement: "self improvement system" (4), "self improvement sub niches" (4), and three single-impression queries. Visible query rows do not identify the two page-level clicks; do not attribute them to the listed zero-click queries.

Preserved the recent revisions of the three traffic pages. Corrected healthy-lifestyle-tips after identifying residual fast-result promises, unsupported symptom attribution, an inaccurate exercise comparison and a universal two-week habit claim. Replaced these with a practical planning checklist, appropriately bounded advice, and direct NIDDK habit-change/NHS fatigue sources checked today. Updated matching FAQ structured data, meta description, registry excerpt and sitemap modification date. Preserved original publication date, URL, images, disclaimer and layout.

This improves editorial reliability, not proof of future indexing, traffic or AdSense acceptance. No broad legacy redirect or site consolidation was performed.

Deployment verification: Pages run 40046153831 succeeded for f298495. A fresh cache-miss request to the revised article returned HTTP 200 and the corrected copy. The canonical URL still returned the old copy with CF-Cache-Status HIT. Cloudflare authentication expired and requires the user's password, so the canonical URL purge and subsequent recrawl request remain pending. Purge https://nichehubpro.com/articles/healthy-lifestyle-tips.html, https://nichehubpro.com/articles.js and https://nichehubpro.com/sitemap.xml, then verify the canonical copy before requesting indexing.

AdSense account inspected today still shows Needs attention / Low value content and ads.txt Not found, with the displayed last-updated date 1 June 2026. Public ads.txt delivery does not mean AdSense has refreshed its account status. No new AdSense review was submitted.

## Cache follow-up completed

After the owner reconnected to the correct Cloudflare account, submitted a successful exact-URL purge for healthy-lifestyle-tips.html, articles.js, api/articles.json and sitemap.xml. No global purge or cache setting change was made. The canonical article now returns HTTP 200 with the final corrected copy, without the old one-week result promise; the first verification returned CF-Cache-Status MISS and Age 0. The public registry contains the revised excerpt and the public sitemap reports 24 October 2026 as this article's lastmod. The earlier cache/authentication blockers above are resolved.

Search Console then confirmed "Indexing requested" for this article and stated it was added to a priority crawl queue. This confirms request acceptance, not completion of a new crawl or a ranking change. Proof: healthy-lifestyle-indexing-requested.png.

## Three-guide editorial batch

Revised healthy-living-tips (constraints and seven care areas), healthy-daily-habits (seven steps to maintain one action), and simple-morning-habits (seven options for the transition after waking). Removed unsupported symptom attribution, universal water/meal/clock prescriptions, fixed improvement deadlines, neurological promises and invented outcome narratives. Each now has one explicitly fictional two-paragraph planning example, five question sections, seven numbered items, three distinct contextual article links and five matching visible/schema FAQs. Preserved original publication dates, canonical URLs, cover and three section images. Removed the oversized repeated related-link blocks from these pages.

Checked NIDDK behaviour-change guidance and NHS fatigue and sleep guidance. Sources are linked with their scope; these checklists are not presented as tested treatments. Synced catalog excerpts and pin metadata, meta descriptions (156/158/156 characters), modification dates and sitemap lastmod. No Make scenario was changed. Verification: python scripts/check_editorial_batch.py passed for all three pages. Publication and canonical cache verification follow deployment; no AdSense review submitted in this batch.

Completion: editorial commit f0087d6 and generated-catalog commit e7b27b2 are on main. GitHub Pages run 40106310838 succeeded. Cloudflare accepted the six-URL purge for the three articles, articles.js, api/articles.json and sitemap.xml. All three canonical pages returned HTTP 200, CF-Cache-Status MISS and the revised text. Public catalog excerpts and all three sitemap lastmod dates were confirmed. Tested the public FAQ accordion successfully.

Individual Search Console inspections still reported Crawled - currently not indexed (previous crawls: living tips 25 September, daily habits 8 September, morning habits 11 October). Each revised URL received one new request, and Google confirmed Indexing requested for all three. Acceptance is not completed indexing or an AdSense approval. Proofs: editorial-batch-purge-success.png, editorial-batch-live-proof.png, healthy-living-indexing-requested.png, healthy-daily-indexing-requested.png and simple-morning-indexing-requested.png.

## Follow-up: morning routine for mental health

Removed the embedded credential from the local origin URL; origin now uses the clean HTTPS repository URL. Read access passed without an interactive prompt. Revocation/replacement of the exposed token still requires the owner; read access alone is not proof of revocation or new authenticated write access.

Reviewed relaxation, emotional burnout and morning-routine guides. The first two already contain substantial earlier revisions and were left unchanged. Corrected remaining unsupported brain, willpower and all-day-control claims in morning-routine-for-mental-health; removed rigid weekly habit schedules, overlong repeated related-link blocks and comparative routine-duration claims. Preserved five sections, four images, original publication date and canonical URL. Added five explicit options, three distinct contextual links, appropriate NIMH/NHS references and matching FAQ/schema. Updated modification date and sitemap lastmod. No automation schedule or Make scenario changed.

Completion: commit c893e6f pushed successfully using the clean origin URL and configured credential helper. This proves current write access, not replacement or revocation of the exposed token. Pages run 40111691651 succeeded. Cloudflare accepted a targeted purge of the article and sitemap. The canonical article returned HTTP 200, CF-Cache-Status MISS, the new introduction and no old ego-depletion claim. Structure, matching five FAQ answers/schema, five numbered options, three unique local links, four images, 160-character meta description, short paragraphs and no em dashes were checked. Purge proof: mental-health-morning-purge-success.png. Token revocation remains an owner action; no new AdSense review or additional indexing request was submitted in this follow-up.

## Editorial follow-up: pressure and daily planning

Reviewed how-to-stay-calm-under-pressure, improve-daily-routine and success-habits. Left success-habits unchanged because it already distinguishes planning from evidence and acknowledges constraints. Revised the other two pages to address separate needs: selecting a safe practical response to immediate demands, and reviewing one recurring schedule bottleneck.

Removed ninety-second regulation claims, unsupported rankings/equivalence of relaxation techniques, brain-offline language, deterministic resilience promises and a fabricated six-week clinical outcome story. Replaced these with five explicit response options, safety boundaries, practical support and a clearly fictional workload example. Checked NHS breathing guidance and NCCIH evidence/cautions; cited these within the article and scoped the references.

Reworked daily routine into five observable planning checks, with a fictional student example rather than a promised energy or productivity result. NIDDK behaviour-change guidance is linked for obstacles and setbacks, without presenting the editorial method as a clinical treatment. Both pages retain canonical URLs, original publication dates and four images. Matching five FAQ answers/schema, three distinct contextual article links, short paragraphs and no em dashes verified. Meta descriptions are 159 and 157 characters. Synced catalog titles/excerpts/pin metadata, read time and sitemap lastmod. No Make, publication schedule or security setting changed. python scripts/check_editorial_batch.py passes for the three preceding guides and these two revisions.

Completion: editorial commit 859967e, generated catalog commit 7830d1e and final related-label correction e6db1a2/merge 76696e4 are published. Pages runs 40117153483 and 40117350273 succeeded. Cloudflare accepted the five-file purge; both canonical pages returned HTTP 200 and the revised text with cache MISS. The public catalog has both new titles and sitemap lastmod is 24 October for both. A final exact-URL purge followed the pressure-page sidebar label correction; public verification confirmed the new label and absence of the old promise.

Individual Search Console inspections reported Crawled - currently not indexed (previous crawl 26 September for pressure, 20 September for routine). Google accepted one new indexing request per revised page; this is not confirmation of indexing or ranking. Proofs: pressure-routine-purge-success.png, pressure-indexing-requested.png and daily-routine-indexing-requested.png. No new AdSense review submitted.

## Immediate sleep-content corrections

Revised how-sleep-affects-mental-health and best-foods-for-better-sleep after the global audit confirmed problematic public passages. Removed unsupported comparisons with medicines, fabricated recovery/tapering narratives, fixed improvement deadlines, hormone/reset claims and unsupported minute/percentage estimates. Both now distinguish practical guidance from diagnosis or treatment and explicitly direct medication decisions to the prescriber. One clearly fictional two-paragraph planning example replaces each outcome story.

Mental-health guide: five areas to describe during assessment, sourced to NHLBI sleep-deficiency guidance and NHS insomnia guidance. Food guide: seven ordinary evening food options, explicitly not a treatment ranking; reflux timing is scoped to people with night-time GERD symptoms using NIDDK guidance. Sources were opened and checked. Preserved canonical URLs, original publication dates and four image assets per article. Rebuilt matching five FAQ answers/schema, five question sections, three distinct contextual article links, short paragraphs and exact disclaimer. Synced titles, 159/160-character descriptions, catalog/pin metadata and sitemap lastmod. All seven articles in scripts/check_editorial_batch.py passed. Publication and canonical verification follow the push; no Make, schedule or AdSense review changed.

Completion: commit 0d9b417 and generated catalog 40a865a deployed in successful Pages run 40125197993. Cloudflare accepted the targeted five-URL purge. Both canonical articles returned HTTP 200, cache MISS and the revised text; both old treatment-related passages were absent. Public catalog titles are correct. The food-guide FAQ accordion was tested on the public page. Proofs: sleep-guides-purge-success.png and sleep-food-guide-live-proof.png. No new indexing request or AdSense review submitted. Updated the local global-audit report to close these two immediate priorities without treating the remaining triage as verified errors.

## Three habit guides: differentiated practical uses

Revised daily-wellness-habits, healthy-morning-routine-checklist and how-to-create-sustainable-healthy-habits. Removed fixed improvement and automaticity timelines, unsupported biological claims, universal water-first prescriptions, compulsory minimum routines and invented symptom/weight-loss outcomes. Sources checked: NIMH self-care guidance and NIDDK behaviour-change guidance. Examples are explicitly fictional and do not claim measured results.

Distinct uses: daily wellness chooses an unmet care need across five areas and includes a need/obstacle/support note; morning checklist offers seven editable prompts with needed/already-handled/not-relevant choices; sustainable habits offers seven maintenance questions and a keep/adapt/pause/stop review note. These are editorial planning tools, not clinically tested packages. All three preserve original publication dates, canonical URLs and four image assets. Synced titles, 156/158/158-character descriptions, catalog/pin metadata and sitemap lastmod. Ten-page scripts/check_editorial_batch.py passed. Publication/canonical verification follows deployment. No Make, schedule, account security or AdSense review changed.

Completion: commit 0a40312 and generated catalog d10b181 deployed in successful Pages run 40136446752. Submitted the six-URL targeted Cloudflare purge. All three canonical articles returned HTTP 200, cache MISS and revised introductions. The checked 30-day improvement promise, two-week energy promise and invented weight-loss story were absent. Public catalog titles are correct. Tested the morning checklist FAQ accordion. Proof: morning-checklist-live-proof.png. Updated the local global-audit report; no indexing request or AdSense review submitted.


## Three mental-wellness guides

Revised how-to-stop-negative-thoughts, how-to-build-confidence and how-to-stop-worrying-about-the-future. Removed unsupported biological explanations, fixed outcome timelines and invented success stories. Replaced them with distinct thought-response options, specific-skill practice and seven planning questions. Linked NHS guidance, labelled fictional examples, preserved original publication dates and image assets, and synchronised FAQ/schema, catalog and sitemap. All thirteen editorial batch checks passed. Deployment and public verification pending.

Completion: editorial commit 3e45b3c and generated catalog 4d637b4 deployed successfully in Pages run 40137212314. Submitted a targeted six-URL cache purge; all three public canonical pages returned HTTP 200 and cache MISS with the new scope text and none of the checked old invented-story markers. Sitemap dates are 2026-10-24. Confidence FAQ expanded correctly in browser. Proof: mental-guides-live-proof.png. No AdSense review or indexing request submitted.

## Broken reference repair

Replaced the retired NHS healthy-eating URL in healthy-lifestyle-tips and how-to-improve-energy-naturally with the verified current eight-tips page. Replaced the misspelled and retired WHO workplace-stress Q&A in how-to-deal-with-stress-at-work with the verified Mental health at work fact sheet; aligned its citation summary with organisational risk prevention and worker support. Clarified that energy-guide references do not validate every method or diagnose fatigue. This is a reference repair, not a completed substantive review of those guides. JSON-LD parsing and absence of old URLs/em dashes checked. Original publication dates preserved; modified/sitemap dates updated where needed.

Completion: reference repair 4221050 deployed in successful Pages run 40138633944. Targeted purge submitted for three article URLs and sitemap. All three public pages returned HTTP 200/cache MISS, contained replacement references and no retired URLs. Replacement NHS and WHO destinations independently returned HTTP 200. Browser proof: reference-repair-live-proof.png. These guides remain in the substantive editorial review backlog, particularly energy and work stress (universal mechanisms and outcome timelines remain outside this link-repair scope).

## Energy and work-stress substantive review

Rewrote how-to-improve-energy-naturally around five information/support checks for fatigue, with NHS/MedlinePlus guidance, care thresholds and no universal exercise or supplement prescription. Rewrote how-to-deal-with-stress-at-work around five support-conversation steps, distinguishing personal pauses from organisational changes; linked WHO, NHS and the explicitly UK HSE framework. Removed fixed recovery promises, biological reset claims, guaranteed energy transformation and therapy-dismissive wording. Fictional examples have no invented measured outcomes. Preserved original publication dates, canonical URLs and four image assets. Catalog and pin metadata synchronised. All fifteen editorial batch checks pass, including FAQ/schema, short paragraphs, unique internal links and 158/159-character descriptions. Public verification follows deployment.
