"""
Request Google/Bing indexing for all current articles via IndexNow.
Run: python ping_indexing.py
"""
import requests, sys
sys.stdout.reconfigure(encoding='utf-8')

SITE_URL     = "https://nichehubpro.com"
SITEMAP      = f"{SITE_URL}/sitemap.xml"
INDEXNOW_KEY = "nichehubpro"

NEW_URLS = [
    f"{SITE_URL}/articles/how-to-stop-overthinking.html",
    f"{SITE_URL}/articles/how-to-calm-anxiety-quickly.html",
    f"{SITE_URL}/articles/signs-of-mental-exhaustion.html",
    f"{SITE_URL}/articles/how-to-stop-negative-thoughts.html",
    f"{SITE_URL}/articles/how-to-reduce-stress-naturally.html",
    f"{SITE_URL}/articles/how-to-relax-your-mind.html",
    f"{SITE_URL}/articles/how-to-deal-with-anxiety-daily.html",
    f"{SITE_URL}/articles/how-to-stop-anxiety-attacks.html",
    f"{SITE_URL}/articles/how-to-control-your-thoughts.html",
    f"{SITE_URL}/articles/how-to-calm-your-mind-instantly.html",
    f"{SITE_URL}/articles/how-to-stop-worrying.html",
    f"{SITE_URL}/articles/how-to-improve-mental-clarity.html",
    f"{SITE_URL}/articles/how-to-feel-calm-instantly.html",
    f"{SITE_URL}/articles/how-to-feel-happy-again.html",
    f"{SITE_URL}/articles/how-to-stop-overthinking-at-work.html",
    f"{SITE_URL}/articles/morning-routine-for-mental-health.html",
    f"{SITE_URL}/articles/anxiety-before-sleep.html",
    f"{SITE_URL}/articles/how-to-sleep-better-naturally.html",
    f"{SITE_URL}/articles/fear-of-failure-anxiety.html",
    f"{SITE_URL}/articles/foods-that-reduce-anxiety.html",
    f"{SITE_URL}/articles/how-to-break-negative-thinking.html",
    f"{SITE_URL}/articles/how-to-increase-energy-naturally.html",
    f"{SITE_URL}/articles/how-to-feel-in-control-of-your-mind.html",
    f"{SITE_URL}/articles/benefits-of-walking-daily.html",
    f"{SITE_URL}/articles/emotional-burnout-recovery.html",
    f"{SITE_URL}/articles/how-to-detox-your-mind.html",
    f"{SITE_URL}/articles/how-to-stay-calm-under-pressure.html",
    f"{SITE_URL}/articles/healthy-daily-habits.html",
    f"{SITE_URL}/articles/signs-of-anxiety-disorder.html",
    f"{SITE_URL}/articles/how-to-focus-without-distractions.html",
    f"{SITE_URL}/articles/simple-morning-habits.html",
    f"{SITE_URL}/articles/how-to-stop-panic-attacks.html",
    f"{SITE_URL}/articles/how-to-stop-procrastination.html",
    f"{SITE_URL}/articles/sleep-routine-tips.html",
    f"{SITE_URL}/articles/how-to-build-confidence.html",
    f"{SITE_URL}/articles/how-to-stay-motivated.html",
    f"{SITE_URL}/articles/healthy-lifestyle-tips.html",
    f"{SITE_URL}/articles/how-to-stop-worrying-about-the-future.html",
    f"{SITE_URL}/articles/time-management-tips.html",
    f"{SITE_URL}/articles/daily-wellness-habits.html",
    f"{SITE_URL}/articles/deep-work-techniques.html",
    f"{SITE_URL}/articles/natural-energy-boosters.html",
    f"{SITE_URL}/articles/how-to-stop-overthinking-at-night.html",
]

# ── 1. Ping Bing with updated sitemap ─────────────────────────────────────
print("1. Pinging Bing with updated sitemap...")
r = requests.get(f"https://www.bing.com/ping?sitemap={SITEMAP}", timeout=10)
print(f"   Bing ping: {r.status_code} {'OK' if r.status_code == 200 else 'Failed'}")

# ── 2. IndexNow — submit all article URLs for indexing ────────────────────
print(f"\n2. Submitting {len(NEW_URLS)} URLs via IndexNow...")
payload = {
    "host":        "nichehubpro.com",
    "key":         INDEXNOW_KEY,
    "keyLocation": f"{SITE_URL}/{INDEXNOW_KEY}.txt",
    "urlList":     NEW_URLS,
}
r = requests.post(
    "https://api.indexnow.org/indexnow",
    json=payload,
    headers={"Content-Type": "application/json"},
    timeout=15,
)
print(f"   IndexNow: {r.status_code} {'OK — indexing requested' if r.status_code in (200, 202) else r.text[:200]}")

print(f"\nDone. {len(NEW_URLS)} article URLs submitted to Bing/Yandex for indexing.")
print("Note: Google discovers URLs via sitemap crawl — no direct ping needed.")
