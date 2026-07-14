# -*- coding: utf-8 -*-
"""
medium_publisher.py
Publishes a NicheHubPro article to Medium via the Integration Token API.

Usage:
  python medium_publisher.py articles/how-to-stop-self-sabotaging.html
  python medium_publisher.py --latest          # publish most recently modified article

Config required in config.py:
  MEDIUM_INTEGRATION_TOKEN = "your_token_here"

Get your token: medium.com → Settings → Security → Integration tokens
"""

import sys, os, re, json, time, argparse
sys.stdout.reconfigure(encoding='utf-8')
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_URL  = "https://nichehubpro.com"

# ── Load config ───────────────────────────────────────────────────────────────
sys.path.insert(0, BASE_DIR)
try:
    import config
    TOKEN = getattr(config, "MEDIUM_INTEGRATION_TOKEN", "")
except ImportError:
    TOKEN = ""

# ── Category → Medium tags ────────────────────────────────────────────────────
TAGS = {
    "mental-wellness":   ["mental health", "anxiety", "wellness", "self improvement", "mindfulness"],
    "productivity":      ["productivity", "self improvement", "habits", "focus", "personal development"],
    "healthy-lifestyle": ["health", "wellness", "healthy living", "lifestyle", "self care"],
}

# ── Content extraction ────────────────────────────────────────────────────────
def extract_article(html_path):
    with open(html_path, encoding="utf-8") as f:
        html = f.read()

    slug = os.path.basename(html_path).replace(".html", "")

    # Title from <h1>
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    title = re.sub(r'<[^>]+>', '', h1.group(1)).strip() if h1 else slug.replace("-", " ").title()

    # Cover image from og:image (already absolute URL)
    og_img = re.search(r'property="og:image"\s+content="([^"]+)"', html)
    if not og_img:
        og_img = re.search(r'content="(https://nichehubpro\.com/images/[^"]+)"', html)
    cover_url = og_img.group(1) if og_img else f"{SITE_URL}/images/{slug}.jpg"

    # Category from breadcrumb JSON-LD
    bc = re.search(r'"item":\s*"https://nichehubpro\.com/(mental-wellness|productivity|healthy-lifestyle)/"', html)
    category = bc.group(1) if bc else "mental-wellness"

    # Meta description
    desc = re.search(r'<meta name="description" content="([^"]+)"', html)
    meta_desc = desc.group(1) if desc else ""

    # Article body (inside <article>...</article>)
    article_m = re.search(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)
    if not article_m:
        return None
    body = article_m.group(1)

    # Clean the body for Medium
    body = clean_body(body, slug, cover_url)

    canonical = f"{SITE_URL}/articles/{slug}.html"

    return {
        "title":     title,
        "cover":     cover_url,
        "category":  category,
        "canonical": canonical,
        "meta_desc": meta_desc,
        "body":      body,
        "slug":      slug,
    }


def clean_body(html, slug, cover_url):
    """Strip site-specific elements and prepare clean HTML for Medium."""

    # Remove table of contents block
    html = re.sub(r'<div[^>]*class="[^"]*toc[^"]*"[^>]*>.*?</div>\s*(?:</div>\s*)*', '', html, flags=re.DOTALL)

    # Remove author-block and author-bio-card
    html = re.sub(r'<div[^>]*class="[^"]*author-(?:block|bio-card)[^"]*"[^>]*>.*?</div>\s*</div>', '', html, flags=re.DOTALL)

    # Remove inline-promo boxes
    html = re.sub(r'<div[^>]*class="[^"]*inline-promo[^"]*"[^>]*>.*?</div>\s*</div>', '', html, flags=re.DOTALL)

    # Remove breadcrumb nav inside article
    html = re.sub(r'<nav[^>]*class="[^"]*breadcrumb[^"]*"[^>]*>.*?</nav>', '', html, flags=re.DOTALL)

    # Convert FAQ accordion to plain Q&A
    def faq_to_plain(m):
        inner = m.group(0)
        questions = re.findall(r'<button[^>]*class="[^"]*faq-q[^"]*"[^>]*>(.*?)</button>', inner, re.DOTALL)
        answers   = re.findall(r'<div[^>]*class="[^"]*faq-a[^"]*"[^>]*>(.*?)</div>', inner, re.DOTALL)
        out = "<h2>Frequently Asked Questions</h2>\n"
        for q, a in zip(questions, answers):
            q_text = re.sub(r'<[^>]+>', '', q).strip()
            out += f"<p><strong>{q_text}</strong></p>\n<p>{a.strip()}</p>\n"
        return out
    html = re.sub(r'<div[^>]*class="[^"]*faq-section[^"]*"[^>]*>.*?</div>\s*(?:</div>\s*)?', faq_to_plain, html, flags=re.DOTALL)

    # Remove disclaimer div (we'll add a plain text version)
    disclaimer_match = re.search(r'<div[^>]*class="[^"]*disclaimer[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
    disclaimer_text = ""
    if disclaimer_match:
        disclaimer_text = re.sub(r'<[^>]+>', '', disclaimer_match.group(1)).strip()
        html = html[:disclaimer_match.start()] + html[disclaimer_match.end():]

    # Remove all <script> and <style> tags
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)

    # Convert relative internal links to absolute
    html = re.sub(r'href="(/[^"]*)"', lambda m: f'href="{SITE_URL}{m.group(1)}"', html)

    # Convert relative image src to absolute
    html = re.sub(r'src="(/images/[^"]+)"', lambda m: f'src="{SITE_URL}{m.group(1)}"', html)

    # Replace <picture><source srcset="...webp"><img src="...jpg"></picture> with simple <img>
    html = re.sub(
        r'<picture[^>]*>.*?<img[^>]+src="([^"]+)"[^>]*>.*?</picture>',
        lambda m: f'<img src="{m.group(1)}" alt="">',
        html, flags=re.DOTALL
    )

    # Remove empty divs and excessive whitespace
    html = re.sub(r'<div[^>]*>\s*</div>', '', html)
    html = re.sub(r'\n{3,}', '\n\n', html)

    # Build the final Medium content:
    # Cover image first, then body, then footer
    content = f'<img src="{cover_url}" alt="">\n\n'
    content += html.strip()

    if disclaimer_text:
        content += f'\n\n<p><em>{disclaimer_text}</em></p>'

    return content


# ── Medium API ────────────────────────────────────────────────────────────────
API_BASE = "https://api.medium.com/v1"

def get_user_id(token):
    r = requests.get(f"{API_BASE}/me",
                     headers={"Authorization": f"Bearer {token}"}, timeout=15)
    r.raise_for_status()
    return r.json()["data"]["id"]


def publish_post(token, user_id, article):
    tags = TAGS.get(article["category"], TAGS["mental-wellness"])
    payload = {
        "title":         article["title"],
        "contentFormat": "html",
        "content":       article["body"],
        "tags":          tags,
        "canonicalUrl":  article["canonical"],
        "publishStatus": "public",
    }
    r = requests.post(
        f"{API_BASE}/users/{user_id}/posts",
        json=payload,
        headers={
            "Authorization":  f"Bearer {token}",
            "Content-Type":   "application/json",
            "Accept":         "application/json",
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["data"]


# ── Main ──────────────────────────────────────────────────────────────────────
def publish(html_path):
    if not TOKEN:
        print("ERROR: MEDIUM_INTEGRATION_TOKEN not set in config.py")
        print("  Get it at: medium.com -> Settings -> Security -> Integration tokens")
        return None

    print(f"  Extracting: {os.path.basename(html_path)}")
    article = extract_article(html_path)
    if not article:
        print("  ERROR: Could not extract article content.")
        return None

    try:
        user_id = get_user_id(TOKEN)
    except Exception as e:
        print(f"  ERROR getting Medium user ID: {e}")
        return None

    try:
        result = publish_post(TOKEN, user_id, article)
        url = result.get("url", "unknown")
        print(f"  Published to Medium: {url}")
        print(f"  Canonical: {article['canonical']}")
        return url
    except requests.HTTPError as e:
        print(f"  ERROR publishing to Medium: {e.response.status_code} {e.response.text[:300]}")
        return None
    except Exception as e:
        print(f"  ERROR: {e}")
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?", help="Path to article HTML file")
    parser.add_argument("--latest", action="store_true", help="Publish the most recently modified article")
    parser.add_argument("--new", action="store_true", help="Publish all articles modified in the last 2 hours")
    args = parser.parse_args()

    articles_dir = os.path.join(BASE_DIR, "articles")

    if args.new:
        cutoff = time.time() - 7200
        files = [
            os.path.join(articles_dir, f)
            for f in os.listdir(articles_dir)
            if f.endswith(".html") and os.path.getmtime(os.path.join(articles_dir, f)) > cutoff
        ]
        if not files:
            print("No new articles in the last 2 hours.")
            return
        for path in sorted(files):
            print(f"Publishing {os.path.basename(path)}...")
            publish(path)
            time.sleep(5)
    elif args.latest:
        files = [os.path.join(articles_dir, f) for f in os.listdir(articles_dir) if f.endswith(".html")]
        if not files:
            print("No articles found.")
            return
        html_path = max(files, key=os.path.getmtime)
        print(f"Latest article: {os.path.basename(html_path)}")
        publish(html_path)
    elif args.file:
        html_path = args.file
        if not os.path.isabs(html_path):
            html_path = os.path.join(BASE_DIR, html_path)
        publish(html_path)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
