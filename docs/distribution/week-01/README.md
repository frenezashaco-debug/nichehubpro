# Week 1 distribution package

Prepared 2026-09-19. **Not scheduled or published on Pinterest or Medium.**

## Contents

- Six Pinterest titles, descriptions, alt texts, tracked links and proposed boards: [pinterest.json](pinterest.json).
- Six distinct 1024 x 1536 PNG images: [workspace image directory](../../../images/social/week-01/).
- Three standalone Medium adaptations: [sleep](medium-sleep.md), [habits](medium-habits.md), [self-care](medium-selfcare.md).
- Image provenance and prompts: [image-prompts.md](image-prompts.md).
- Repeatable read-only structural checks: [verify.py](verify.py).

The Medium drafts are about 600 words each, not replacements for the longer website articles. They provide a separate practical angle and a contextual link to the source guide. Drafts and images were prepared with AI assistance. They are not medical review or evidence of personal experience.

## Proposed release dates

| Guide | Pinterest A + Medium | Pinterest B | Board |
|---|---|---|---|
| Sleep routine | September 21 | September 28 | Healthy Lifestyle |
| Building habits | September 23 | September 30 | Productivity |
| Daily self-care | September 24 | October 1 | Healthy Lifestyle |

Timezone: Africa/Casablanca. No time has been selected or scheduled. These dates are proposals; move them if final review or account access is incomplete.

## Editorial changes to the website

- Sleep: seven explicit options matching the title, contextual links, corrected conflicting publication badge, removed arbitrary 20-minute wording from the FAQ question.
- Habits: five explicit planning steps, contextual links, replaced unnecessary dopamine discussion and a misleading example about replacing a snack.
- Self-care: less rigid sleep and hydration advice, optional rather than compulsory habits, revised FAQ, practical support and professional-care limits, corrected breadcrumb, visible source heading.
- Sleep and self-care: removed the long auto-inserted related-link tail; retained the three selected links.
- All three: modification date and sitemap lastmod updated for substantive revisions. Original publication dates retained.

This is a focused editorial pass on these three pages, not an assertion that the entire site is free of low-value content or ready for AdSense approval.

## Checks performed

Run from the project root:

```powershell
python docs/distribution/week-01/verify.py
```

Verified locally: six distinct images with 2:3 dimensions; Pin copy lengths; tracked destinations; three unique canonicals; one H1 and five FAQ items per page; parseable JSON-LD; matching modification dates; existing HTML link destinations; sitemap entries; publication generation still paused.

Sources consulted:

- [NHLBI: Insomnia treatment](https://www.nhlbi.nih.gov/health/insomnia/treatment), for routine limits and clinical-care context.
- [NIDDK: Changing habits](https://www.niddk.nih.gov/health-information/diet-nutrition/changing-habits-better-health), for planning and setbacks.
- [NIMH: Caring for mental health](https://www.nimh.nih.gov/health/topics/caring-for-your-mental-health), for flexible self-care and seeking support.

## Account access and release gate

On September 19, both public profiles opened successfully, but Pinterest displayed “Se connecter” and Medium displayed “Sign in”. No authenticated publishing session was available. The proposed board names were observed on the public Pinterest profile; board IDs and scheduling features have not been verified.

Before release:

1. The owner reads and approves the three adaptations and revised website pages. Do not describe this automated review as human or medical validation.
2. Confirm the deployed pages reflect the changes, their images load, and FAQ controls work.
3. Sign in to the intended Pinterest and Medium accounts in the connected browser.
4. Check existing drafts and scheduled posts to avoid duplicates. Select the proposed existing boards and confirm a publication time.
5. Keep source attribution and an honest AI-assistance disclosure. For an actual republication, set Medium's canonical field to the original URL without UTM parameters; these adaptations are standalone pieces, so do not blindly assign a canonical without deciding whether they are equivalent content.
6. After scheduling, record actual dates and platform URLs. A local proposed date is not proof of scheduling.

The old Pinterest and Medium publisher scripts were not run. Automatic website article generation remains disabled. No paid promotion, subscriptions or new account permissions were enabled.
