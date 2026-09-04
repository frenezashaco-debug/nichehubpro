# Editorial remediation batch

This is the fixed order for content remediation before the next AdSense review.
It is based on `site_quality_audit.py`, which scores unsupported numerical and
health claims, vague institutional citations, and technical integrity problems.

## Completion rule for every article

An article is only marked complete after all of the following are true:

1. Every factual health or research claim has either been removed or linked to
   a precise, direct primary or public-health source.
2. Generic home-page citations and invented authority references are removed.
3. The title, meta description, introduction, FAQ, and Pinterest copy make no
   promise of an outcome or use unsupported numbers.
4. It includes practical guidance, clear limits, and, where relevant, advice
   to seek qualified care for persistent, severe, or urgent symptoms.
5. `python site_quality_audit.py` records a materially lower risk score and
   there are no broken local links or image assets.

## Wave 1 - active now

1. `why-most-people-fail-at-building-habits.html`
2. `best-focus-techniques-for-students.html`
3. `best-morning-habits-for-more-energy.html`
4. `healthy-morning-routine-checklist.html`
5. `best-routine-planner-methods.html`

## Wave 2

6. `how-to-improve-mental-clarity.html`
7. `how-to-build-confidence-through-discipline.html`
8. `benefits-of-walking-every-day.html`
9. `how-to-build-a-stress-resistant-morning-routine.html`
10. `pomodoro-technique-explained-for-beginners.html`

## Wave 3

11. `how-to-build-a-better-lifestyle-long-term.html`
12. `how-to-improve-concentration-naturally.html`
13. `how-to-stay-productive-every-day.html`
14. `why-you-feel-lost-in-life.html`
15. `healthy-habits-for-busy-people.html`

## Wave 4

16. `signs-of-mental-burnout-and-how-to-recover.html`
17. `healthy-daily-routine-checklist.html`
18. `simple-morning-habits.html`
19. `daily-self-care-routine.html`
20. `healthy-productivity-habits-for-entrepreneurs.html`

## Wave 5

21. `life-balance-habits.html`
22. `best-self-improvement-systems-explained.html`
23. `why-discipline-beats-motivation.html`
24. `best-evening-habits-for-better-sleep.html`
25. `success-habits.html`

## Guardrails

- Scheduled and manual automated publishing remain paused in `batch_24weeks.py`.
- New drafts must pass `publisher_v2.py` source validation.
- The review queue is regenerated with `python site_quality_audit.py`; generated
  reports remain local and are not published to the website.
- The older legacy pages are already largely `noindex`. Do not mass-delete or
  redirect remaining pages until each source and target URL is mapped.
