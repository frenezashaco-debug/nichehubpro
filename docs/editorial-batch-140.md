# Editorial batch: 140 articles

First pass applied September 18, 2026; publication resumed September 19.

- Scope: 140 articles, excluding the four articles in commit `b4d6182`.
- Modified: 137 article files, plus the two article catalogs.
- Changes: individually selected less exaggerated titles, synchronized H1/social/schema/breadcrumb titles, and corrections to misleading internal-link labels.
- Publication dates and sitemap dates were preserved because this was primarily a title and metadata pass.
- Scheduled article publishing remains paused.

## Review still required

The automated audit identifies 557 candidate passages across 129 articles. These are leads for editorial verification, not 557 proven false statements. All 140 articles still require individual review of evidence, originality, and health advice. This batch is not a complete rewrite or an AdSense approval assessment.

The latest audit snapshot is in `reports/batch-140/register.json` and `reports/batch-140/register.md`. Its `modified_articles: 0` means the read-only audit made no changes; it does not describe the preceding applied batch.

Run `python scripts/editorial_batch_140.py` to check titles, JSON-LD, local article links and transformation idempotence and rebuild the review register. Use `--apply` only to apply the documented title/link transformations. No publishing clients or credentials are loaded.

Next editorial priorities: confidence, anxiety management, mental rest, pressure, and calming techniques. Verify the full claim against a primary or institutional source, then rewrite or remove unsupported claims in context. Adding a source link alone is insufficient.
