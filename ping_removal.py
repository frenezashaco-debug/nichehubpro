"""
Notify search engines about removed URLs using:
1. Google sitemap ping (re-crawl updated sitemap)
2. IndexNow API (instant removal signal to Bing/Yandex)

Run: python ping_removal.py
"""
import requests, time, sys
sys.stdout.reconfigure(encoding='utf-8')

SITE_URL  = "https://nichehubpro.com"
SITEMAP   = f"{SITE_URL}/sitemap.xml"

# Old directories that were deleted
REMOVED_URLS = [
    f"{SITE_URL}/anti-aging-foods-to-eat-daily/",
    f"{SITE_URL}/benefits-of-daily-meditation-for-anxiety/",
    f"{SITE_URL}/benefits-of-drinking-lemon-water-in-the-morning/",
    f"{SITE_URL}/benefits-of-journaling-for-mental-health/",
    f"{SITE_URL}/benefits-of-magnesium-for-sleep-and-health-2/",
    f"{SITE_URL}/benefits-of-spending-less-time-on-your-phone/",
    f"{SITE_URL}/benefits-of-spending-time-in-nature/",
    f"{SITE_URL}/benefits-of-strength-training-for-women/",
    f"{SITE_URL}/benefits-of-taking-probiotics-daily/",
    f"{SITE_URL}/benefits-of-therapy-and-counseling/",
    f"{SITE_URL}/benefits-of-walking-30-minutes-a-day/",
    f"{SITE_URL}/benefits-of-yoga-for-mental-health/",
    f"{SITE_URL}/best-anti-inflammatory-foods-to-eat-daily/",
    f"{SITE_URL}/best-evening-routine-for-better-sleep-and-recovery/",
    f"{SITE_URL}/best-foods-for-brain-health/",
    f"{SITE_URL}/best-foods-for-healthy-skin-and-hair/",
    f"{SITE_URL}/best-free-productivity-apps-2026/",
    f"{SITE_URL}/best-free-tools-for-productivity-in-2025/",
    f"{SITE_URL}/best-morning-drinks-for-energy/",
    f"{SITE_URL}/best-productivity-apps-for-students-2026/",
    f"{SITE_URL}/best-stretches-for-lower-back-pain/",
    f"{SITE_URL}/calendar-blocking-vs-to-do-lists-which-is-better/",
    f"{SITE_URL}/cold-shower-benefits-and-how-to-start/",
    f"{SITE_URL}/coping-with-loneliness/",
    f"{SITE_URL}/grounding-techniques-for-anxiety/",
    f"{SITE_URL}/healing-from-childhood-trauma/",
    f"{SITE_URL}/healthy-habits-to-start-in-your-20s/",
    f"{SITE_URL}/healthy-meal-prep-for-beginners/",
    f"{SITE_URL}/how-to-avoid-burnout-as-an-entrepreneur/",
    f"{SITE_URL}/how-to-avoid-distractions-while-studying/",
    f"{SITE_URL}/how-to-be-happy-alone-without-feeling-lonely/",
    f"{SITE_URL}/how-to-break-bad-habits-for-good/",
    f"{SITE_URL}/how-to-build-a-consistent-work-from-home-routine/",
    f"{SITE_URL}/how-to-build-a-daily-routine-that-works/",
    f"{SITE_URL}/how-to-build-a-healthy-bedtime-routine/",
    f"{SITE_URL}/how-to-build-a-morning-routine-that-sticks/",
    f"{SITE_URL}/how-to-build-a-personal-knowledge-management-system/",
    f"{SITE_URL}/how-to-build-a-positive-mindset/",
    f"{SITE_URL}/how-to-build-a-workout-habit-that-sticks/",
    f"{SITE_URL}/how-to-build-emotional-resilience/",
    f"{SITE_URL}/how-to-build-healthy-eating-habits/",
    f"{SITE_URL}/how-to-build-muscle-at-home-without-equipment/",
    f"{SITE_URL}/how-to-build-self-confidence/",
    f"{SITE_URL}/how-to-cope-with-change-and-uncertainty/",
    f"{SITE_URL}/how-to-cope-with-grief-and-loss/",
    f"{SITE_URL}/how-to-create-a-distraction-free-environment/",
    f"{SITE_URL}/how-to-create-a-personal-productivity-system/",
    f"{SITE_URL}/how-to-create-a-productive-home-office-setup/",
    f"{SITE_URL}/how-to-deal-with-grief-and-loss/",
    f"{SITE_URL}/how-to-deal-with-rejection/",
    f"{SITE_URL}/how-to-detox-your-body-naturally/",
    f"{SITE_URL}/how-to-eat-healthy-on-a-budget/",
    f"{SITE_URL}/how-to-fix-a-bad-sleep-schedule/",
    f"{SITE_URL}/how-to-focus-better-when-working-from-home/",
    f"{SITE_URL}/how-to-get-things-done-when-overwhelmed/",
    f"{SITE_URL}/how-to-improve-cardiovascular-health-naturally/",
    f"{SITE_URL}/how-to-improve-digestion-naturally/",
    f"{SITE_URL}/how-to-improve-gut-health-in-30-days/",
    f"{SITE_URL}/how-to-improve-sleep-quality-naturally/",
    f"{SITE_URL}/how-to-improve-your-metabolism-naturally/",
    f"{SITE_URL}/how-to-improve-your-posture-while-sitting/",
    f"{SITE_URL}/how-to-manage-anger-effectively/",
    f"{SITE_URL}/how-to-manage-anger-without-suppressing-it/",
    f"{SITE_URL}/how-to-meditate-when-you-cant-sit-still/",
    f"{SITE_URL}/how-to-overcome-negative-self-talk/",
    f"{SITE_URL}/how-to-overcome-perfectionism/",
    f"{SITE_URL}/how-to-plan-your-week-effectively/",
    f"{SITE_URL}/how-to-plan-your-week-on-sunday/",
    f"{SITE_URL}/how-to-practice-box-breathing-for-stress-relief/",
    f"{SITE_URL}/how-to-quit-caffeine-without-headaches/",
    f"{SITE_URL}/how-to-reduce-cortisol-naturally/",
    f"{SITE_URL}/how-to-reduce-inflammation-with-diet/",
    f"{SITE_URL}/how-to-reduce-screen-time-before-bed/",
    f"{SITE_URL}/how-to-reduce-stress-naturally/",
    f"{SITE_URL}/how-to-reduce-sugar-cravings-naturally/",
    f"{SITE_URL}/how-to-set-healthy-boundaries/",
    f"{SITE_URL}/how-to-sleep-8-hours-and-wake-up-refreshed/",
    f"{SITE_URL}/how-to-stop-emotional-eating/",
    f"{SITE_URL}/how-to-stop-feeling-lazy-and-unmotivated/",
    f"{SITE_URL}/how-to-stop-negative-thoughts-at-night/",
    f"{SITE_URL}/how-to-stop-overthinking-at-night/",
    f"{SITE_URL}/how-to-stop-snacking-at-night/",
    f"{SITE_URL}/how-to-stop-worrying-about-the-future/",
    f"{SITE_URL}/how-to-track-your-goals-effectively/",
    f"{SITE_URL}/how-to-use-affirmations-that-actually-work/",
    f"{SITE_URL}/how-to-use-the-two-minute-rule-to-get-things-done/",
    f"{SITE_URL}/how-to-work-smarter-not-harder/",
    f"{SITE_URL}/inbox-zero-method-explained/",
    f"{SITE_URL}/magnesium-benefits-for-sleep-and-anxiety/",
    f"{SITE_URL}/mindfulness-exercises-for-beginners/",
    f"{SITE_URL}/perfectionism-and-anxiety-how-to-break-the-cycle/",
    f"{SITE_URL}/second-brain-method-explained/",
    f"{SITE_URL}/signs-of-a-codependent-relationship/",
    f"{SITE_URL}/signs-of-burnout-and-how-to-recover/",
    f"{SITE_URL}/signs-of-depression-in-adults/",
    f"{SITE_URL}/signs-of-depression-you-should-not-ignore/",
    f"{SITE_URL}/signs-of-emotional-exhaustion/",
    f"{SITE_URL}/signs-of-generalized-anxiety-disorder/",
    f"{SITE_URL}/signs-of-unresolved-trauma/",
    f"{SITE_URL}/sleep-hygiene-tips-for-better-rest/",
    f"{SITE_URL}/stretching-routine-for-desk-workers/",
    f"{SITE_URL}/time-management-tips-for-students/",
    f"{SITE_URL}/toxic-productivity-what-it-is-and-how-to-avoid-it/",
    f"{SITE_URL}/weekly-review-routine-to-stay-on-track/",
    f"{SITE_URL}/what-causes-low-self-esteem-and-how-to-fix-it/",
    f"{SITE_URL}/what-is-cognitive-behavioral-therapy/",
    f"{SITE_URL}/what-to-eat-before-and-after-a-workout/",
]

# ── 1. Ping Google with updated sitemap ───────────────────────────────────
print("1. Pinging Google with updated sitemap...")
r = requests.get(f"https://www.google.com/ping?sitemap={SITEMAP}", timeout=10)
print(f"   Google ping: {r.status_code} {'OK' if r.status_code == 200 else 'Failed'}")

# ── 2. Ping Bing with updated sitemap ─────────────────────────────────────
print("2. Pinging Bing with updated sitemap...")
r = requests.get(f"https://www.bing.com/ping?sitemap={SITEMAP}", timeout=10)
print(f"   Bing ping: {r.status_code} {'OK' if r.status_code == 200 else 'Failed'}")

# ── 3. IndexNow — notify Bing of removed URLs ─────────────────────────────
print(f"\n3. Sending {len(REMOVED_URLS)} removed URLs via IndexNow...")
INDEXNOW_KEY = "nichehubpro"  # simple key — must match file at /nichehubpro.txt
payload = {
    "host": "nichehubpro.com",
    "key": INDEXNOW_KEY,
    "keyLocation": f"{SITE_URL}/{INDEXNOW_KEY}.txt",
    "urlList": REMOVED_URLS
}
r = requests.post(
    "https://api.indexnow.org/indexnow",
    json=payload,
    headers={"Content-Type": "application/json"},
    timeout=15
)
print(f"   IndexNow: {r.status_code} {'OK' if r.status_code in (200, 202) else r.text[:100]}")

print(f"\nDone. Google will re-crawl your sitemap and drop the 107 old URLs faster.")
