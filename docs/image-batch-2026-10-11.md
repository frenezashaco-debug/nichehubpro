# Article image restoration, 2026-10-11

23 articles now have a cover plus three inline illustrations. Added 70 image elements: 69 inline images and one previously missing cover. Article text, headings, sources, FAQs, publication dates and existing covers were preserved.

Existing topic-specific assets were visually inspected in contact sheets. Five unsuitable inline assets were replaced with newly generated illustrations. The remaining 64 inline images and the restored cover reuse existing assets. No originals were overwritten or removed.

All inserted inline images are WebP files under 100,000 bytes, with descriptive alt text, intrinsic dimensions, lazy loading, async decoding and responsive width/auto height. Larger existing assets received separate `-inline-v1.webp` copies. The restored cover is eager/high priority.

## New files and generation prompts

Built-in imagegen was used. Common prompt: one landscape 16:9 editorial illustration, photorealistic natural wellness lifestyle photography, soft warm window light, uncluttered realistic environment, natural skin texture, shallow depth of field, sharp subject, no stock posing, no text, lettering, logos, watermark, graphic overlays or collage, no medical treatment implications.

Scene prompts and saved paths:

- `images/best-free-productivity-apps-for-android-2026-sec1-inline-v1.webp`: relatable middle-aged man at a light oak kitchen table comparing a single Android phone with a paper notebook; screen angled away, no readable interface, deciding on a task app.
- `images/best-free-productivity-apps-for-android-2026-sec3-inline-v1.webp`: woman in her forties at a sunlit home desk setting a smartphone face down beside a closed laptop, making space for focused work, unposed side view.
- `images/best-free-productivity-apps-for-android-2026-sec5-inline-v1.webp`: young adult with curly hair reviewing a paper weekly plan at a bright home workspace with one phone nearby, thoughtful candid side view, no readable writing.
- `images/why-anxiety-feels-physical-sec1-inline-v1.webp`: adult woman by a living-room window, hand resting on her lap, slightly tense shoulders and concerned expression, everyday moment, one person only.
- `images/deep-work-techniques-sec1-inline-v1.webp`: woman at a bright home office pausing work to glance at one phone beside a laptop, mildly distracted, candid side angle.

These are illustrations, not documentary evidence of real patients or app screenshots. No claims of clinical effectiveness are inferred from them.

## Verification

- `scripts/restore_article_images.cjs` verifies all 23 targets, four images per page, asset decoding and inline size budget. Its `--apply` mode is idempotent and checks that non-image content remains unchanged.
- `scripts/check_health_fixes.py` passed for 165 sitemap pages and local links/assets.
- Local-file browser preview was blocked by the browser URL policy. No bypass was attempted. Responsive CSS was checked in source; visual mobile verification remains outstanding.
- Production deployment must be checked separately after push. No Cloudflare purge, publication workflow or Make webhook was triggered.

Four images is a project presentation standard, not an AdSense eligibility requirement or a content-quality guarantee.
