# -*- coding: utf-8 -*-
"""
fix_section_images.py
Finds articles missing section images and regenerates them using Claude + HF FLUX.

Usage:
  python fix_section_images.py              # scan all, fix missing
  python fix_section_images.py --slug how-to-build-self-discipline  # fix one
"""

import os, re, sys, time, io, json, argparse
sys.stdout.reconfigure(encoding='utf-8')
import requests
from PIL import Image

try:
    from config import ANTHROPIC_API_KEY, HF_API_KEY
except ImportError:
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    HF_API_KEY        = os.environ.get("HF_API_KEY", "")

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
ARTICLES_DIR = os.path.join(BASE_DIR, "articles")
IMAGES_DIR   = os.path.join(BASE_DIR, "images")
SITE_URL     = "https://nichehubpro.com"

_HF_API_URL  = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
_HF_RULES    = "Real skin texture, natural imperfections, shallow depth of field. Photorealistic. No text, no logos, no watermarks, no AI look, no man."


def get_missing_section_slugs():
    """Return slugs of articles that are missing any sec1/sec3/sec5 webp."""
    missing = []
    for fname in sorted(os.listdir(ARTICLES_DIR)):
        if not fname.endswith(".html"):
            continue
        slug = fname[:-5]
        has_all = all(
            os.path.exists(os.path.join(IMAGES_DIR, f"{slug}-sec{n}.webp"))
            for n in (1, 3, 5)
        )
        if not has_all:
            missing.append(slug)
    return missing


def extract_article_info(slug):
    """Pull title and category from article HTML."""
    path = os.path.join(ARTICLES_DIR, f"{slug}.html")
    if not os.path.exists(path):
        return None, None
    with open(path, encoding="utf-8") as f:
        html = f.read()
    title_m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    title    = re.sub(r'<[^>]+>', '', title_m.group(1)).strip() if title_m else slug.replace("-", " ").title()
    tag_m    = re.search(r'<span class="article-tag">([^<]+)</span>', html)
    category = tag_m.group(1).strip() if tag_m else "Mental Wellness"
    return title, category


def generate_prompts_via_claude(title, category):
    """Ask Claude to produce 3 section image prompts for the article."""
    import anthropic, httpx
    client = anthropic.Anthropic(
        api_key=ANTHROPIC_API_KEY,
        http_client=httpx.Client(verify=False),
    )
    system = (
        "You generate humanized photo prompts for wellness article section images. "
        "Rules: always a young woman 25-35 shown from shoulders/collarbone up only — no hands, no objects. "
        "Never a man. Real skin texture, messy hair, plain clothing. Candid not posed. "
        "Each image must show a different scene, setting, and expression from the others. "
        "Flat natural window light. Shot on 50mm or 85mm f/1.8-2.8. "
        "NO text, NO logos, NO watermarks, NO AI smooth skin, NO studio lighting."
    )
    prompt = (
        f'Generate 3 section image prompts for a wellness article titled: "{title}" (category: {category}).\n'
        "Return a JSON array with exactly 3 objects:\n"
        '[{"section_index": 0, "prompt": "...", "alt_text": "..."}, '
        '{"section_index": 2, "prompt": "...", "alt_text": "..."}, '
        '{"section_index": 4, "prompt": "...", "alt_text": "..."}]\n'
        "Each prompt must be detailed, specific, and show a different candid moment relevant to the article topic.\n"
        "Return ONLY the JSON array."
    )
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": prompt}]
    )
    text = msg.content[0].text.strip()
    m = re.search(r'\[.*\]', text, re.DOTALL)
    return json.loads(m.group(0)) if m else []


def generate_section_image(prompt, slug, sec_num, retries=4):
    """Download a single section image from HF FLUX."""
    filename = f"{slug}-sec{sec_num}.webp"
    out_path = os.path.join(IMAGES_DIR, filename)
    full_prompt = f"{prompt} {_HF_RULES}"

    for attempt in range(1, retries + 1):
        try:
            print(f"    Attempt {attempt} for sec{sec_num}...")
            resp = requests.post(
                _HF_API_URL,
                headers={"Authorization": f"Bearer {HF_API_KEY}"},
                json={"inputs": full_prompt, "parameters": {"width": 1024, "height": 576}},
                verify=False,
                timeout=180,
            )
            resp.raise_for_status()
            img = Image.open(io.BytesIO(resp.content)).convert("RGB")
            img = img.resize((800, 450), Image.LANCZOS)
            buf = io.BytesIO()
            for q in range(82, 10, -5):
                buf = io.BytesIO()
                img.save(buf, format="WEBP", quality=q, method=4)
                if buf.tell() / 1024 <= 80:
                    break
            with open(out_path, "wb") as f:
                f.write(buf.getvalue())
            print(f"    Saved: {filename} ({os.path.getsize(out_path)//1024}KB)")
            return filename
        except Exception as e:
            print(f"    Attempt {attempt} failed: {e}")
            if attempt < retries:
                time.sleep(20)
    return None


def inject_section_images(slug, section_images):
    """Insert section img tags into the article HTML if not already there."""
    path = os.path.join(ARTICLES_DIR, f"{slug}.html")
    with open(path, encoding="utf-8") as f:
        html = f.read()

    changed = False
    for sec_idx, info in section_images.items():
        sec_num  = sec_idx + 1
        filename = info["filename"]
        alt      = info["alt_text"]
        img_tag  = (
            f'\n      <img src="../images/{filename}" '
            f'alt="{alt}" '
            f'style="width:100%;max-height:480px;object-fit:cover;border-radius:10px;margin:28px 0 20px;display:block;" '
            f'width="1920" height="1080" loading="lazy">\n'
        )
        # Already present?
        if filename in html:
            print(f"  sec{sec_num} already in HTML — skipping injection")
            continue

        # Insert after the corresponding h2 section (id="sec-{sec_num}")
        pattern = re.compile(
            rf'(<h2 id="sec-{sec_num}"[^>]*>.*?</h2>\s*.*?)(\n      <h2|\n      <div class="inline-promo"|</article>)',
            re.DOTALL
        )
        m = pattern.search(html)
        if m:
            insert_pos = m.end(1)
            html = html[:insert_pos] + img_tag + html[insert_pos:]
            print(f"  Injected sec{sec_num} image after h2#sec-{sec_num}")
            changed = True
        else:
            print(f"  Could not find injection point for sec{sec_num} — skipping")

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
    return changed


def fix_slug(slug):
    print(f"\nFixing: {slug}")
    title, category = extract_article_info(slug)
    if not title:
        print(f"  Article HTML not found — skipping")
        return False

    print(f"  Title: {title}")
    print(f"  Category: {category}")

    # Determine which section images are missing
    missing_nums = [n for n in (1, 3, 5) if not os.path.exists(os.path.join(IMAGES_DIR, f"{slug}-sec{n}.webp"))]
    if not missing_nums:
        print(f"  All section images already exist — skipping")
        return False

    print(f"  Missing sections: {missing_nums}")
    print(f"  Generating prompts via Claude...")
    prompts = generate_prompts_via_claude(title, category)
    if not prompts:
        print("  Failed to generate prompts")
        return False

    section_images = {}
    sec_num_map = {0: 1, 2: 3, 4: 5}

    for item in prompts:
        sec_idx = item.get("section_index", 0)
        sec_num = sec_num_map.get(sec_idx, sec_idx + 1)
        if sec_num not in missing_nums:
            continue
        prompt  = item.get("prompt", "")
        alt     = item.get("alt_text", title)
        print(f"  Generating sec{sec_num}...")
        filename = generate_section_image(prompt, slug, sec_num)
        if filename:
            section_images[sec_idx] = {"filename": filename, "alt_text": alt}
        time.sleep(20)

    if not section_images:
        print("  No section images generated")
        return False

    inject_section_images(slug, section_images)
    print(f"  Done: {len(section_images)} image(s) fixed")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", help="Fix a specific article slug")
    args = parser.parse_args()

    if args.slug:
        slugs = [args.slug]
    else:
        slugs = get_missing_section_slugs()
        if not slugs:
            print("All articles have section images. Nothing to fix.")
            return
        print(f"Found {len(slugs)} article(s) with missing section images:")
        for s in slugs:
            print(f"  - {s}")

    fixed = 0
    for slug in slugs:
        if fix_slug(slug):
            fixed += 1

    print(f"\nDone. {fixed}/{len(slugs)} articles fixed.")


if __name__ == "__main__":
    main()
