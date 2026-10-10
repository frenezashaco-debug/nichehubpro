# Website readiness batch

Run from the project directory:

```powershell
python scripts/readiness_batch.py --live --pagespeed
node scripts/check_analytics.cjs
```

The batch writes `reports/readiness/latest.json` and `latest.md`. It does not publish articles, request indexing, or send Pinterest pins. Reports are intentionally ignored by Git. Local working-copy findings may include unpublished edits.

## Results on 10 October 2026

- 165 sitemap URLs and 148 articles examined.
- No missing local page/link/image targets, canonical mismatches, noindex conflicts, or H1-count issues detected by this check.
- 23 articles contain fewer than four image elements. This is a project-format issue, not a Google eligibility requirement or a verdict on content value.
- Seven sampled production URLs returned HTTP 200, including the latest blood-sugar, dopamine and attention articles, the homepage, category page, sitemap and ads.txt.
- GitHub reports successful publishing runs on 8 and 9 October. This alone does not confirm successful Make/Pinterest distribution or source accuracy.
- PageSpeed API returned HTTP 429 for both requests. No performance score was obtained.
- Analytics tests cover opt-in, decline, existing opt-out, repeat initialization and blocked browser storage. Browser visual QA remains to be done.

## Changes in this batch

- Added a repeatable local/live audit and machine-readable page-level findings.
- Optional GA4 now waits for explicit analytics consent. The persistent Privacy choices button permits changing the choice. Advertising consent stays denied in this script.
- Ebook uses the shared analytics consent flow.
- Privacy policy describes this behavior. This analytics control is not a Google-certified advertising CMP.

## Next batch, ordered

1. Verify AdSense CMP configuration and actual browser consent behavior using the authenticated account. Do not mark this done based on the analytics button.
2. Inspect Make history for the latest slug, confirm resulting pins and configure durable deduplication before any replay.
3. Review claims throughout the five previously flagged articles. Citation-section cleanup is not a full medical fact-check.
4. Review the 23 image-count findings; choose topic-specific visuals where they add value.
5. Obtain mobile PageSpeed results when quota is available, then prioritize measured bottlenecks.
6. Export Search Console queries and pages; prioritize existing impressions and useful internal links before adding publication volume.

Google reference for analytics implementation: https://developers.google.com/tag-platform/security/guides/consent?consentmode=basic
