# Second editorial batch

Status October 16: all ten local revisions completed and tested. This is not an AdSense eligibility certification. Deployment is tracked separately below.

## Completed locally

`how-to-sleep-better-naturally`: replaced unsupported percentages, fixed recovery timelines, thermostat cutoffs, breathing holds, and fictional recovery testimony. Added an original planning worksheet and clearly illustrative scenario. Distinguished habits from insomnia treatment. Preserved the page shell, four images and five accordion FAQs; synchronized FAQ structured data. These are editorial changes, not a clinical review.

Sources consulted October 15, 2026:
- https://www.nhlbi.nih.gov/health/insomnia/treatment
- https://www.nhlbi.nih.gov/health/sleep-deprivation/healthy-sleep-habits

## Nine additional revisions completed October 16

1. foods-that-reduce-anxiety
2. how-to-increase-energy-naturally
3. how-to-feel-calm-instantly
4. natural-energy-boosters
5. the-psychology-behind-why-deadlines-make-you-more-productive
6. how-to-build-energy-that-lasts-all-day-without-crashing
7. why-hydration-affects-your-focus-more-than-you-think
8. healthy-habits-for-busy-people
9. healthy-productivity-habits-for-entrepreneurs

Five guides received rewritten main sections, examples, conclusions and FAQs: instant calm, increasing energy, busy people, entrepreneurs, and deadlines. Four received targeted consistency fixes and practical planning additions: food/anxiety, natural energy boosters, all-day energy, and hydration. These four retain earlier text and are not comprehensive clinical reviews.

Removed cold immersion and straining instructions for anxiety, universal hormone and recovery claims, invented improvement testimonials, and unsupported performance guarantees. Food/anxiety now has five topic-specific FAQ answers rather than two generic ones. All ten preserve four images and the existing page layout classes. Titles, descriptions, reading times, FAQ schema, catalogue entries, future pin copy, and sitemap modification dates were synchronized. No Pinterest request was sent.

Additional sources checked:
- https://www.nhs.uk/mental-health/self-help/guides-tools-and-activities/breathing-exercises-for-stress/
- https://www.nccih.nih.gov/health/relaxation-techniques-what-you-need-to-know
- https://www.nhs.uk/symptoms/chest-pain/
- https://medlineplus.gov/ency/article/003088.htm
- https://medlineplus.gov/dehydration.html
- https://www.nhs.uk/live-well/eat-well/food-guidelines-and-food-labels/the-eatwell-guide/
- https://www.nimh.nih.gov/health/publications/generalized-anxiety-disorder-gad
- https://www.niddk.nih.gov/health-information/diet-nutrition/changing-habits-better-health
- https://www.hse.gov.uk/stress/standards/demands.htm
- https://www.nhs.uk/live-well/exercise/physical-activity-guidelines-for-adults-aged-19-to-64/
- https://www.cdc.gov/healthy-weight-growth/water-healthy-drinks/index.html

The deadline article no longer relies on broad neuroscience claims. Its planning exercises are explicitly editorial suggestions, not experimentally validated methods.

## Checks and remaining work

- Local health/link/assets check: 167 pages passed before integrating the October 16 automatic article.
- Ten-guide regression test passed: metadata/catalogues, image counts, FAQ schema, anchors, and targeted removed claims.
- Earlier ten-guide and five-guide regression checks passed.
- Eight publication-blocker tests and three Pages-wait tests passed. The former needed an unsandboxed rerun because the Windows sandbox denied temporary-directory access.
- Visual preview could not be performed: browser policy blocks local file URLs. No alternate access route was used. Actual consent display and choices remain untested.
- Remote commit `730d1f3` shows that the October 16 article generation/push occurred. This alone does not establish full workflow or Pinterest success.
- Preserve existing user edits in the dopamine and blood-sugar articles.

## Reproduction notes

`apply_second_batch.cjs` is a guarded one-time migration against the old article text, not a routine publisher step. `second_batch_content.cjs` contains its authored replacements. `finalize_second_batch.cjs` is safe to rerun for this fixed batch. Run `node scripts/test_second_batch.cjs` after changes; do not rerun the migration on already revised pages.
