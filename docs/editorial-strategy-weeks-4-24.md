# NicheHubPro Editorial Strategy

## Objective

Build topical authority in Mental Wellness, Productivity, and Healthy Lifestyle while improving the quality signals that matter for organic search and AdSense review.

The plan remains 72 articles across 24 weeks, but production is handled in controlled editorial batches instead of unattended automatic publishing.

## Current position

- The 24-week plan contains 72 planned articles.
- 9 planned articles are already present and reviewed.
- The next planned content starts at Day 10.
- The publishing guard remains active: `PUBLISHING_PAUSED = True`.
- Production format: five articles per editorial batch, followed by fact review, technical QA, commit, deployment, and indexing requests.
- The five most recently reviewed articles are already pushed in commit `a064c16`.

## Editorial principles

1. Solve a clearly defined reader problem before targeting a keyword.
2. Avoid overlapping articles that compete for the same search intent.
3. Use one primary keyword, a small group of supporting terms, and one clear reader promise.
4. Treat mental-health and nutrition claims as YMYL content. Use cautious wording, precise institutional sources, and clear limits.
5. Never invent experts, credentials, studies, statistics, quotations, or personal results.
6. Use fictional scenarios only when they are explicitly labelled as illustrative.
7. Prefer a useful 1,800 to 2,400-word article over padded length. Pillar guides may reach 3,500 to 4,500 words when the subject genuinely requires it.
8. Keep every article human, specific, readable, and free of em dashes, watermarks, generic AI phrasing, and unsupported guarantees.
9. Every article must help another article through internal links. A cluster is more valuable than a series of isolated posts.
10. No new article is published until it passes the human source and originality review.

## Batch workflow

Each batch contains five articles and follows this order:

### Step 1: Editorial brief

For every topic, record:

- primary keyword and search intent;
- reader problem and expected answer;
- supporting keywords and questions;
- competing or overlapping URLs already on the site;
- target word range;
- internal links in and out;
- source requirements and health-safety limits;
- meta title, meta description, URL slug, and schema type.

### Step 2: Source map

Use two or three sources only when they directly support a claim. Prefer:

- NIMH for anxiety, stress, symptoms, and when to seek help;
- CDC for stress, sleep, and general wellbeing guidance;
- NHLBI or CDC for sleep and sleep routines;
- NIDDK for habits, nutrition, and behavior change;
- NIH or PubMed for a specific primary study when the article truly needs one;
- NHS or another national health service for plain-language safety guidance.

Do not link to a home page as proof of a specific claim. Link to the exact institutional page. If an exact claim cannot be verified, rewrite it as a practical suggestion or remove it.

### Step 3: Human rewrite

Use the following article shape:

1. A direct opening that names the reader's problem.
2. A short answer or TL;DR near the top.
3. Five or six question-based sections.
4. Practical steps, limits, and a realistic example.
5. Five useful FAQ answers.
6. A warm conclusion with one action for today.
7. A visible disclaimer on health-related content.
8. A source block with exact links and no unsupported summary statistics.

### Step 4: QA gate

Before staging a batch, check:

- article is at least 1,800 words unless the subject is intentionally brief;
- meta description is 155 to 160 characters;
- title, H1, canonical, Open Graph description, and JSON-LD description agree;
- no em dash, watermark, fake expert, invented quote, or unverifiable statistic;
- no medical diagnosis, treatment promise, supplement dosage, or medication advice without qualified context;
- internal links resolve and use descriptive anchors;
- images have topic-specific alt text, dimensions, and no text overlays;
- `git diff --check`, Python compilation, and the site audit pass;
- only the intended five article files are staged.

### Step 5: Release and measurement

After the human review:

1. Commit the five files as one editorial batch.
2. Push to GitHub and wait for the Pages deployment.
3. Test the five live URLs, canonical tags, sitemap inclusion, and redirects.
4. Request indexing for the five URLs in Search Console.
5. Do not judge performance before enough impressions accumulate. Review CTR, queries, indexing, and engagement after 28 days.

## Next batch: Batch 8, Days 10 to 14

This batch completes Week 4 and starts the science and habits cluster. It is the recommended next release because the five articles connect naturally and avoid publishing five unrelated subjects together.

### 1. How to Stop Feeling Guilty for Resting

- Category: Mental Wellness
- Primary keyword: `feeling guilty for resting`
- Intent: informational and practical
- Promise: explain why rest can feel uncomfortable and provide a low-pressure way to recover without turning rest into another performance task
- Target: 1,900 to 2,200 words
- Source direction: CDC mental-health and stress guidance; NIMH topic pages where symptoms or professional support are discussed
- Safety limit: do not claim that rest alone treats burnout, depression, or anxiety
- Internal links: chronic stress, stress-resistant morning routine, emotional burnout recovery, healthy sleep habits
- CTA: Calm Focus System after the first practical exercise and at the end

### 2. How to Recover Focus After a Distraction

- Category: Productivity
- Primary keyword: `recover focus after a distraction`
- Intent: practical productivity
- Promise: give a short reset sequence for noticing the interruption, choosing the next action, and protecting the next focus block
- Target: 1,800 to 2,100 words
- Source direction: use direct research only for attention-switching claims; otherwise present the sequence as a tested productivity method, not a universal neuroscience fact
- Safety limit: remove exact recovery-time claims unless the exact study and context are cited
- Internal links: protect focus from interruptions, deep work, time blocking, notification system
- CTA: 30-Day Discipline Reset after the recovery sequence

### 3. How to Build Energy That Lasts All Day Without Crashing

- Category: Healthy Lifestyle
- Primary keyword: `energy that lasts all day`
- Intent: practical wellbeing
- Promise: connect sleep, regular meals, hydration, movement, and caffeine timing without promising a fixed energy result
- Target: 2,000 to 2,300 words
- Source direction: CDC sleep guidance, NIDDK nutrition guidance, and cautious caffeine language
- Safety limit: no claims that a food, supplement, or routine “fixes” fatigue; advise medical review for persistent or unexplained fatigue
- Internal links: hydration and focus, healthy sleep habits, natural energy boosters, sustained-energy nutrition
- CTA: Healthy Lifestyle newsletter block after the meal and sleep checklist

### 4. What Neuroplasticity Means for Changing Your Habits

- Category: Mental Wellness
- Primary keyword: `neuroplasticity and habit change`
- Intent: explanatory and practical
- Promise: explain brain change in plain language without implying that every habit rewires the brain on a fixed schedule
- Target: 2,000 to 2,400 words
- Source direction: NIH or NIMH material on learning, habits, and behavior; use primary research only when the article names a specific mechanism
- Safety limit: no “21 days,” “rewire instantly,” or guaranteed brain-change claims
- Internal links: habit formation, daily routine, self-sabotaging, mental toughness
- CTA: 30-Day Discipline Reset in the section about repetition and environment

### 5. The Science of Habit Formation Explained Simply

- Category: Productivity
- Primary keyword: `how habits form`
- Intent: explanatory and practical
- Promise: explain cue, behavior, context, repetition, reward, and adjustment in a way readers can apply to one habit
- Target: 2,000 to 2,400 words
- Source direction: NIMH Habit PVS and NIDDK behavior-change guidance
- Safety limit: no fixed habit timeline, no claim that habits make up a precise percentage of daily behavior, and no promise that a tracker guarantees consistency
- Internal links: habit tracker methods, habits that stick, systems without motivation, daily routine
- CTA: 30-Day Discipline Reset after the habit design worksheet

## Following batch sequence

### Batch 9: Days 15 to 19

Finish the science cluster with body-clock and attention topics, then introduce cognitive load. Rename or soften any title that implies a universal best exercise time or a guaranteed brain-training effect.

### Batch 10: Days 20 to 24

Cover deadlines, sleep, routine, motivation, and gut health. Nutrition and sleep articles must use direct sources and avoid causal claims such as “gut health causes anxiety” or “sleep debt permanently damages performance.”

### Batch 11: Days 25 to 29

Build the high-performance cluster around mental energy, deep work, recovery, and weekly planning. Keep the language sustainable rather than aspirational or “high performer” focused.

### Batch 12: Days 30 to 34

Complete high-performance content with active recovery, sustained nutrition, mental stamina, and proactive resilience. Every health article needs a limits section and professional-support note where appropriate.

### Batch 13: Days 35 to 39

Begin the digital-challenges phase. Replace strong claims such as “rewiring anxiety” with evidence-safe wording such as “how notifications can increase stress and fragment attention.” AI content must discuss verification, privacy, dependency, and the limits of generated answers.

### Batches 14 to 16: Days 40 to 48

Build the digital wellbeing cluster: information overload, AI workflows, digital minimalism, phone boundaries, online comparison, notifications, and a gentle unplugging plan. Avoid moralizing technology use or recommending extreme detoxes.

### Batches 17 to 20: Days 49 to 60

Build advanced systems: decision-making, sustainable discipline, habit architecture, reflection, resilience, and health tracking. These articles should link back to the earlier practical guides rather than repeat them.

### Batches 21 to 24: Days 61 to 72

Publish the pillar guides only after the supporting clusters are stable. Each cornerstone guide must:

- link to at least eight relevant existing articles;
- cite only sources that support the exact claims made;
- include a clear table of contents;
- summarize the practical framework in a downloadable or printable format;
- become the primary internal-link destination for its cluster;
- avoid padding, repeated advice, and unsupported “ultimate” promises.

## Decisions to apply to future titles

Use safer replacements when a title contains a strong scientific or medical promise:

| Avoid | Use instead |
|---|---|
| rewiring your anxiety | managing notification-related stress |
| detox your brain | reduce information overload |
| dopamine detox | reduce quick-reward distractions |
| fix blood sugar crashes | build steadier meal and energy routines |
| gut health controls mood | what gut health may and may not tell you about wellbeing |
| willpower runs out | design routines when motivation is low |
| best time for everyone | how to test timing around your own energy |
| guaranteed habit change | a practical habit experiment |

## Success criteria for the next 90 days

- Every new article passes human source review before publication.
- No new article contains a fabricated expert, study, number, or result.
- The five-article batches improve indexing without creating new 404s or duplicate canonicals.
- Internal links form three visible clusters instead of isolated pages.
- Search Console impressions and CTR are reviewed by page and query after 28 days.
- AdSense review is requested only after the site has a stable, trustworthy body of reviewed content, a working consent solution, and no unresolved quality warnings.
