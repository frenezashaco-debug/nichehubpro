# -*- coding: utf-8 -*-
"""
ping_indexing.py
Submits new/updated articles to Bing, Yandex, Naver, Seznam via IndexNow.

Google /ping?sitemap= deprecated June 2023 — Google indexing is handled
automatically via the sitemap.xml + static internal links we already have.
Bing sitemap ping (410 Gone) — replaced by IndexNow protocol.

Usage:
  python ping_indexing.py              # submit all articles
  python ping_indexing.py --new-only   # submit only articles modified in last 24h
"""

import sys, os, re, json, time, argparse, datetime, warnings
sys.stdout.reconfigure(encoding='utf-8')
import requests
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

SITE_URL     = "https://nichehubpro.com"
INDEXNOW_KEY = "nichehubpro"
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))


# ── LOAD URLS FROM articles.js ────────────────────────────────────────────────
def load_all_urls():
    js_path = os.path.join(BASE_DIR, "articles.js")
    if not os.path.exists(js_path):
        return []
    content = open(js_path, encoding="utf-8").read()
    m = re.search(r'const ARTICLES = (\[[\s\S]*?\]);', content)
    if not m:
        return []
    arts = json.loads(m.group(1))

    static = [
        f"{SITE_URL}/",
        f"{SITE_URL}/mental-wellness/",
        f"{SITE_URL}/productivity/",
        f"{SITE_URL}/healthy-lifestyle/",
        f"{SITE_URL}/all-articles/",
        f"{SITE_URL}/about/",
    ]
    article_urls = [f"{SITE_URL}/articles/{a['slug']}.html" for a in arts]
    return static + article_urls


def load_new_urls(hours=24):
    """Return URLs for articles modified in the last N hours. Falls back to all URLs."""
    all_urls = load_all_urls()
    cutoff = time.time() - hours * 3600
    new = []
    for url in all_urls:
        fname = url.replace(f"{SITE_URL}/articles/", "")
        if not fname.endswith(".html"):
            continue
        fpath = os.path.join(BASE_DIR, "articles", fname)
        if os.path.exists(fpath) and os.path.getmtime(fpath) > cutoff:
            new.append(url)
    return new if new else all_urls


# ── INDEXNOW ──────────────────────────────────────────────────────────────────
_ENDPOINTS = [
    "https://api.indexnow.org/indexnow",
    "https://www.bing.com/indexnow",
]
_BATCH = 100

def submit_indexnow(urls):
    print(f"Submitting {len(urls)} URLs via IndexNow...")
    payload_base = {
        "host":        "nichehubpro.com",
        "key":         INDEXNOW_KEY,
        "keyLocation": f"{SITE_URL}/{INDEXNOW_KEY}.txt",
    }
    submitted = 0
    for i in range(0, len(urls), _BATCH):
        batch = urls[i:i + _BATCH]
        payload = {**payload_base, "urlList": batch}
        for ep in _ENDPOINTS:
            try:
                r = requests.post(
                    ep, json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=20, verify=False
                )
                ok = r.status_code in (200, 202)
                host = ep.split('/')[2]
                print(f"  [{host}] batch {i // _BATCH + 1}: HTTP {r.status_code} "
                      f"{'OK' if ok else r.text[:120]}")
                if ok:
                    submitted += len(batch)
                    break
            except Exception as e:
                print(f"  [{ep}] error: {e}")
        if i + _BATCH < len(urls):
            time.sleep(1)
    return submitted


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--new-only", action="store_true",
                        help="Only submit articles modified in last 24h")
    args = parser.parse_args()

    if args.new_only:
        urls = load_new_urls(hours=24)
        print(f"New/updated in last 24h: {len(urls)} URLs")
    else:
        urls = load_all_urls()
        print(f"Loaded {len(urls)} URLs from articles.js")

    if not urls:
        print("No URLs found — check articles.js exists.")
        return

    submitted = submit_indexnow(urls)
    print(f"\nDone. {submitted}/{len(urls)} URLs submitted to IndexNow.")
    print(f"Timestamp: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")


if __name__ == "__main__":
    main()
