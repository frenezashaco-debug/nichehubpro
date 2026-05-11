"""
Auto-push 3 Pinterest pins for the most recently published article.
Called by GitHub Actions AFTER git push so images are live on the site.
"""
import re, json, requests, sys, time
sys.stdout.reconfigure(encoding='utf-8')

try:
    from config import MAKE_PINTEREST_WEBHOOK
except ImportError:
    print("ERROR: config.py missing or MAKE_PINTEREST_WEBHOOK not set."); sys.exit(0)

if not MAKE_PINTEREST_WEBHOOK:
    print("MAKE_PINTEREST_WEBHOOK not configured — skipping."); sys.exit(0)

SITE_URL    = "https://nichehubpro.com"
RAW_URL     = "https://raw.githubusercontent.com/frenezashaco-debug/nichehubpro/main"
BOARD_IDS = {
    "Mental Wellness":   "1135118349771004496",
    "Productivity":      "1135118349771004499",
    "Healthy Lifestyle": "1135118349771004501",
}

# ── Load articles.js ───────────────────────────────────────────────────────────
try:
    with open("articles.js", "r", encoding="utf-8") as f:
        content = f.read()
    m = re.search(r'const ARTICLES = (\[[\s\S]*?\]);', content)
    if not m:
        print("ERROR: Could not parse articles.js"); sys.exit(1)
    articles = json.loads(m.group(1))
except Exception as e:
    print(f"ERROR reading articles.js: {e}"); sys.exit(1)

if not articles:
    print("No articles found."); sys.exit(0)

# ── Get the most recently added article (first in list = newest) ──────────────
article = articles[0]
slug     = article["slug"]
title    = article["title"]
category = article["category"]
pins     = article.get("pins", [])

if not pins:
    print(f"No pin data for '{slug}' — skipping Pinterest."); sys.exit(0)

# ── Build payload ──────────────────────────────────────────────────────────────
pin_images = [
    f"{RAW_URL}/images/{slug}.jpg",
    f"{RAW_URL}/images/{slug}-sec1.webp",
    f"{RAW_URL}/images/{slug}-sec3.webp",
]

enriched_pins = []
for i, pin in enumerate(pins[:3]):
    enriched_pins.append({
        "title":       pin.get("title", title),
        "description": pin.get("description", ""),
        "image_url":   pin_images[i],
    })

payload = {
    "slug":        slug,
    "title":       title,
    "category":    category,
    "board_id":    BOARD_IDS.get(category, ""),
    "article_url": f"{SITE_URL}/articles/{slug}.html",
    "pins":        enriched_pins,
}

# ── Send ───────────────────────────────────────────────────────────────────────
print(f"Sending 3 Pinterest pins for: {slug}")
try:
    r = requests.post(MAKE_PINTEREST_WEBHOOK, json=payload, timeout=20)
    if r.status_code in (200, 204):
        print(f"OK — 3 pins sent to Make.com for [{category}] board.")
    else:
        print(f"FAILED — status {r.status_code}: {r.text[:200]}")
except Exception as e:
    print(f"ERROR: {e}")
