"""
Auto-push 3 Pinterest pins for the most recently published article.
Called by GitHub Actions AFTER git push so images are live on the site.
"""
import re, json, requests, sys, time
from distribution_payload import build_pinterest_payload
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

try:
    from config import MAKE_PINTEREST_WEBHOOK
except ImportError:
    print("ERROR: config.py missing or MAKE_PINTEREST_WEBHOOK not set."); sys.exit(0)

if not MAKE_PINTEREST_WEBHOOK:
    print("MAKE_PINTEREST_WEBHOOK not configured — skipping."); sys.exit(0)

SITE_URL    = "https://nichehubpro.com"
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
try:
    payload = build_pinterest_payload(article, Path(__file__).resolve().parent)
except (ValueError, OSError) as exc:
    print(f"Pinterest preparation failed: {exc}; Make was not called.")
    sys.exit(1)
enriched_pins = payload['pins']
pin_images = [pin['image_url'] for pin in enriched_pins]

# ── Send ───────────────────────────────────────────────────────────────────────
# A git push does not prove that GitHub Pages has deployed. Check all assets
# before sending anything to Make. Do not retry a POST with an unknown outcome.
for public_url in [payload["canonical_url"], *(pin["image_url"] for pin in enriched_pins)]:
    ready = False
    last_status = 'no response'
    for attempt in range(40):
        try:
            check = requests.get(public_url, timeout=20)
            expected = "image/" if public_url in pin_images else "text/html"
            last_status = f'HTTP {check.status_code}, type {check.headers.get("Content-Type", "missing")}'
            if check.status_code == 200 and expected in check.headers.get("Content-Type", ""):
                ready = True
                break
        except requests.RequestException as exc:
            last_status = type(exc).__name__
        time.sleep(15)
    if not ready:
        print(f"Publication asset not ready: {public_url} ({last_status}); Make was not called.")
        sys.exit(1)

print(f"Sending 3 Pinterest pins for: {slug}")
try:
    r = requests.post(MAKE_PINTEREST_WEBHOOK, json=payload, timeout=20)
    if r.status_code in (200, 204):
        print(f"OK — 3 pins sent to Make.com for [{category}] board.")
    else:
        print(f"Make rejected the request (HTTP {r.status_code}).")
        sys.exit(1)
except Exception as e:
    print("Make request failed; check its execution history before retrying.")
    sys.exit(1)
