# Article corpus corrections, 17 October 2026

## Scope and evidence

All 151 local articles were checked. The canonical public URLs also returned 151 successful responses before this deployment. That public check found zero em dashes and zero occurrences of the unwanted `Images in this article are AI-generated illustrations` caption. The confirmed watermark was in an image's pixels.

The correction data contains 535 specific paragraph/list/FAQ targets across 85 guides, following the initial 15 targeted corrections. These are editorial corrections to identified passages, not a certification that every statement in the corpus is scientifically verified. Changes include removal of invented percentages, unsupported research attributions, fixed recovery deadlines, brain-rewiring guarantees and generic cold-exposure advice. Glucose symptoms are no longer presented as proof of a routine food-induced crash, and a balanced meal is no longer offered as a universal response to hypoglycaemia. Dopamine explanations distinguish the scope of neuroscience from observations about an individual habit.

All 151 articles now have four `<img>` elements, five visible accordion FAQ answers, valid JSON-LD, and FAQ structured answers matching the visible text. Three articles with only two generic FAQs received topic-specific questions. Existing layout, sidebars and stylesheet were retained. Missing paragraph/list closures were made explicit where detected.

## Root cause and future generation

`clean_ai_text.py` previously changed scientific terms, including `elevated` to `improved` and `significantly` to `greatly`. Those broad synonym substitutions have been removed. The cleaner now handles only explicit project style bans and forbidden dash encodings, preserving statistical/medical wording, links and structured data.

The generator now requests exactly five question-based sections and exactly three section-image prompts for indices 0, 2 and 4. Contradictory instructions that forced every image to be a young woman's head-and-shoulders portrait have been removed. Every prompt explicitly prohibits text, watermarks and logos.

The existing automatic publication mode remains in place. A new visual screening call inspects the four assets before public HTML/catalogue registration. A flagged image, duplicate asset, incomplete response, invalid JSON or API failure prevents publication. This adds one multimodal model request to a publication and can reject an otherwise acceptable image. Visual screening is an automated heuristic and can miss defects; a prompt or model approval cannot certify image provenance.

Research attributions, percentages and selected biological claims require a nearby link to a listed source in generated copy. A citation's presence is a traceability check, not proof that the linked paper supports the sentence.

## Image replacements

Contact sheets covered 686 distinct local files referenced by image and responsive-source URLs, including JPEG/WebP alternatives. Five offending scenes were replaced using the built-in imagegen tool, followed by visual inspection and WebP/JPEG encoding below 100 KB per file. Original assets remain recoverable; consuming references now point to versioned replacements.

| Article | Replacement asset |
| --- | --- |
| Future worry | `images/how-to-stop-worrying-about-the-future-sec1-clean-v2.webp` |
| Entrepreneur routines | `images/healthy-productivity-habits-for-entrepreneurs-sec1-clean-v2.webp` |
| Pressure | `images/how-to-stay-calm-under-pressure-sec1-clean-v2.webp` |
| Procrastination | `images/how-to-stop-procrastination-sec5-clean-v2.webp` |
| Discipline cover | `images/how-to-build-discipline-clean-v2.jpg` and `.webp` |

Final prompt set: built-in generation, not CLI fallback.

1. Future worry: "Use case: photorealistic-natural. Create a NEW replacement editorial lifestyle photograph for the article 'How to Stop Worrying About the Future', inline section describing recognizing worry. Wide 16:9 landscape composition. A relatable adult man around 45 with natural skin texture and slightly greying curly hair sits at a small kitchen table beside a sunlit open window, pausing with his palms resting loosely on the table, looking outside with a thoughtful concerned expression. A closed plain notebook lies at the far side of the table, no visible writing. Muted cream shirt, warm cream walls, one small plant, tidy ordinary lived-in room. Candid unposed moment, soft warm natural window light, shallow depth of field, professional documentary wellness photography, sharp natural details, no glamour retouching. No text, no logos, no watermarks, no signatures, no graphic overlays, no branded clothing, no collage. This must be a fresh photograph, not a reconstruction of any previous portrait."
2. Entrepreneurs: "Photorealistic natural editorial lifestyle photograph, wide 16:9. For an inline section about healthy productivity habits for entrepreneurs and setting manageable priorities: a relatable woman around 58 with short salt-and-pepper hair sits at a small wooden home-office desk, calmly arranging three plain unmarked index cards into a short row. She wears a simple unbranded rust-coloured cardigan, natural skin texture, candid concentration, no posed smile. A closed laptop with its back entirely out of frame, one small plant, warm cream walls, soft morning window light, shallow depth of field, clean ordinary room. Show her action and surroundings, not a glamour portrait. No text, no letters, no logos, no watermarks, no signatures, no graphic overlays, no branded clothing. Plain cards must be blank."
3. Pressure: "Photorealistic natural editorial lifestyle photograph, wide 16:9. For an inline section about recognizing pressure and choosing a manageable next task: a relatable adult man around 28 with close-cropped black hair and a plain sage-green sweatshirt sits at an ordinary home office desk, leaning back slightly and pausing with both hands loosely resting on the desk as he looks at a closed blank folder. His expression is concerned and thoughtful, unposed, natural skin texture. No computer visible, no phone, no writing. Warm soft side-window daylight, tidy cream room with one wooden shelf, shallow depth of field, professional documentary photography, everyday realism. No text, no words, no logos, no watermarks, no signatures, no graphic overlays."
4. Procrastination: "Photorealistic natural editorial lifestyle photograph, wide 16:9. For an inline section about making starting a task easier when procrastinating: a relatable adult woman around 38 with dark wavy shoulder-length hair, natural skin texture and a plain unbranded cream long-sleeve top, seated at a modest dining table opening a plain blank notebook and setting a pencil beside it, about to begin. The visible pages are completely blank. No laptop or phone. Candid body language with quiet tentative focus, not posing. Soft warm afternoon window light, ordinary tidy apartment kitchen behind her, shallow depth of field, realistic professional lifestyle photograph. No text, no letters, no logos, no watermarks, no signatures, no graphic overlays, no branded clothing."
5. Discipline: "Photorealistic natural editorial lifestyle photograph, wide 16:9. Main cover for 'How to Build Discipline', depicting practical preparation rather than superhero willpower: a relatable adult man around 62 with silver hair, subtle wrinkles and a plain faded blue cotton shirt stands beside a small entryway table, calmly placing a plain unbranded pair of walking shoes next to a folded jacket in preparation for the next day. The person and action are both clearly visible, natural unposed body language and thoughtful ordinary expression. Warm natural early-evening window light, tidy modest home entryway, shallow depth of field, natural skin and fabric detail, documentary wellness photography. All shoes and clothing completely unbranded. No computers or screens. No text, no words, no logos, no watermarks, no signatures, no graphic overlays."
6. Discipline targeted revision: "Precise object edit. Keep the man, his identity, hands, body pose, blue shirt, warm entryway scene, lighting and composition unchanged. Replace BOTH sports shoes on the table completely with a matching pair of very plain tan canvas slip-on walking shoes, entirely unbranded and unmarked. No shoe tongue labels, no lettering, no stitched symbols, no logos, no decorative marks anywhere on the shoes. They must look like simple anonymous everyday slip-on shoes. Keep hands naturally arranging the pair. All image must remain photorealistic. No text, no logos, no watermarks, no signatures, no graphic overlays."

## Verification and remaining work

- `node scripts/check_corpus_corrections.cjs`: all 151 article structure/style/FAQ checks.
- `python scripts/check_health_fixes.py`: 168 site pages, assets and local destinations.
- Prior first/second-batch checks and removed-claim regression checks.
- 11 publication-blocker tests, 5 visual-response tests and 4 copy-preservation tests; no live Anthropic request is made by these unit tests.

The broad keyword audit still records 216 leads in 69 articles. Many are internal-link labels, negated claims or appropriately scoped scientific terms. These leads are retained for review and must not be described as 216 confirmed errors, or silently treated as verified facts. Not every linked paper or every remaining scientific sentence has received independent source verification. The reports are under `reports/` and are intentionally untracked.

Primary sources consulted include [NIMH anxiety guidance](https://www.nimh.nih.gov/health/publications/generalized-anxiety-disorder-gad), [NHLBI sleep deficiency](https://www.nhlbi.nih.gov/health/sleep-deprivation), [NIDDK low blood glucose](https://www.niddk.nih.gov/health-information/diabetes/overview/preventing-problems/low-blood-glucose-hypoglycemia), [NHS hypoglycaemia](https://www.nhs.uk/conditions/low-blood-sugar-hypoglycaemia/), and the [2010 dopamine review](https://pubmed.ncbi.nlm.nih.gov/21144997/). The neuroscience review is not a clinical trial of digital-detox advice.

Deployment status is verified separately after pushing. No AdSense review request, Pinterest resend or manual Cloudflare purge is part of this correction.
