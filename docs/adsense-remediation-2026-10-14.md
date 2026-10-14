# AdSense remediation: scoped batch

## Implemented locally

- Corrected five links in the cognitive-load article from the nonexistent why-feel-mentally-drained.html to the existing why-you-feel-mentally-drained.html. Corrected the rewrite script too.
- Synchronized 59 catalogue category values with the category actually displayed by each article. This is consistency repair, not an endorsement of every existing category choice.
- Changed the catalogue generator to prefer the explicit article category rather than guessing from title keywords.
- Kept the prior cognitive-load title/summary repair in the catalogue.
- Clarified the editorial policy: automated drafting and technical checks are not individual medical review or proof of factual accuracy. No reviewer identity or qualifications invented.

## Verification

- scripts/check_health_fixes.py: PASS across 166 sitemap pages, local links/assets and existing targeted editorial checks.
- scripts/check_claim_regressions.cjs: PASS for five previously edited articles.
- Explicit-category parsing test: PASS for the attention article (Productivity).
- scripts/audit_editorial_overlap.cjs: 149 article bodies scanned; zero exact repeated paragraphs of 25 or more words in the tested main-prose scope. Boilerplate exclusions and exact matching mean this does not establish semantic originality.
- Existing broad quality audit flags 146 articles for possible review. Its keyword matches include qualified statements and disclaimers, so this is NOT a count of low-value articles or confirmed factual errors.

## Still required

- Review originality and source-to-claim support article by article. This batch does not fix or certify all content.
- Test the already-published European consent message on the live site; dashboard publication alone is insufficient.
- AdSense displays low-value-content rejection and stale/not-found ads.txt status. Do not mark all issues resolved or request review on the basis of this batch.
- Two preexisting article edits (blood sugar and dopamine) were preserved, not rewritten or clinically reviewed here.
- These changes have not been pushed in this batch.

Official guidance: https://support.google.com/adsense/answer/9724?hl=en
