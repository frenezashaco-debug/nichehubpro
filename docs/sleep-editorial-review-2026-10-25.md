# Sleep guide review, 25 October 2026

## Scope

Full revisions of:

- `anxiety-before-sleep`
- `how-to-fall-asleep-when-your-mind-wont-stop`
- `how-to-fix-your-sleep-schedule`

Removed the untraceable 2023 early-recognition statistic, fixed three-to-seven-day reset claims, one-to-two-week improvement promises, the claim that fatigue proves progress, and blanket claims about needing or not needing medication. Kept the distinction between general preparation and individually guided treatment. Preserved the original publication dates and canonical URLs.

The three guides have different purposes: an evening concern handoff, a wakefulness/treatment discussion card, and a sleep-opportunity map. Examples are explicitly fictional and do not claim a result. Metadata, five question sections, five FAQ answers and JSON-LD were checked. Incoming recommendation labels were synchronised with the new titles; other article prose was not revised by that label pass.

## Sources checked

- [NHS: Tackling your worries](https://www.nhs.uk/every-mind-matters/mental-wellbeing-tips/self-help-cbt-techniques/tackling-your-worries/): practical versus hypothetical concerns.
- [NHS: Sleep problems](https://www.nhs.uk/every-mind-matters/mental-health-issues/sleep/): sleep difficulties and daytime effects.
- [NHLBI: Insomnia treatment](https://www.nhlbi.nih.gov/health/insomnia/treatment): CBT-I and the limits of reproducing treatment through a general article.
- [NHLBI: Insomnia diagnosis](https://www.nhlbi.nih.gov/health/insomnia/diagnosis): assessment and useful sleep-diary information.
- [NHLBI: Circadian rhythm disorders treatment](https://www.nhlbi.nih.gov/health/circadian-rhythm-disorders/treatment): individual treatment and the significance of light-therapy timing.
- [NHS: Insomnia](https://www.nhs.uk/conditions/insomnia/): avoid driving when sleepy.

## Image inspection and replacement

Fifteen original file variants were inspected on a contact sheet. Selected images were also opened at original resolution. No visible text or watermark was observed in those inspections; this is not a pixel-level certification of the whole image library.

The exaggerated-expression image in the anxiety guide was replaced with a new, separately named asset. The original remains unchanged. Built-in imagegen was used; the selected output was inspected, encoded as WebP without changing its composition, and inspected again.

- Active asset: `images/anxiety-before-sleep-sec1-clean-v2.webp`
- Size: 72,260 bytes; dimensions: 1672 by 941 pixels.
- Alt: Man sitting on the edge of a bed beside a window in the early evening.

Final generation prompt:

> Use case: photorealistic-natural. Asset type: wide section photograph for a factual wellbeing article about anxiety before sleep. Generate a brand-new candid editorial lifestyle photograph, not an edit or a collage. A relatable man in his early forties sits sideways on the edge of a modest tidy bed at home in the early evening, looking thoughtfully toward a softly lit window, hands resting naturally on his knees, gently pensive expression with normal relaxed eyes. Medium-wide landscape composition, realistic skin texture and ordinary clothing, warm natural window light balanced with a small bedside lamp, uncluttered bedroom, shallow depth of field. He looks like an ordinary person pausing after the day, not a model or a clinical patient. Avoid exaggerated fear, wide startled eyes, fake smiles, plastic skin, medical devices, yoga poses, dramatic before-and-after framing. No text, letters, logos, signatures, graphic overlays or watermarks anywhere. No book covers, screens or labels. Natural anatomy and proportions, professional photographic quality. Target composition 16:9.

## Validation

All 58 full-revision guides passed `scripts/check_editorial_batch.py`. The shared inventory checks passed for 154 descriptions and FAQ/schema pairs, with the two pre-existing user-modified articles preserved. Public deployment verification is recorded after release in the project progress notes.

This batch does not certify the other 96 articles' full scientific content or all images on the site. It does not submit an AdSense review, request indexing or modify Make.
