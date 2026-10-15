# Pre-publication blockers

- Added dependency-free publication_checks.py, called by validate_article_quality during generation and again before publication/image generation.
- Checks body HTML, intro, summary, conclusion, headings and FAQ, plus internal_links/related slugs.
- Rejects nonexistent local destinations, including old WordPress paths; accepts existing canonical article files and site directories.
- Adds narrow regression patterns for previously observed dangerous claims and leaked editing instructions.
- Percentages require an inline HTTPS citation in the same block matching a declared reference. This is traceability only, not source retrieval or factual verification.
- Rejects selected numeric outcome constructions in illustrative examples. This does not detect every fictional testimonial or semantic variation.
- Eight offline tests pass. Python syntax compilation passes. Existing ten-article regression tests and 167-page local link/asset checks pass.
- GitHub workflow runs blocker tests before generation. Schedule unchanged. No additional workflow permission or human approval gate introduced.

Limitations: regex checks can miss paraphrases or reject quoted warnings. Fragment IDs, external source availability, clinical accuracy, originality and actual consent behavior are not certified. A blocked draft is not silently published. No live generation/API test was triggered.

Remaining work: the second editorial batch of ten articles and a real consent-flow test. Do not infer AdSense readiness from these checks.
