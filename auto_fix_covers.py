"""
auto_fix_covers.py — Post-publish safety net.

Scans all articles for:
  1. Pillow fallback covers (< 100 KB) → regenerates with DALL-E 3
  2. Missing section images → generates + injects into HTML

Run after batch_30days.py in the CCR agent, and locally whenever needed.
"""
import sys, os, io, time, requests, re
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR   = os.path.join(BASE_DIR, "images")
ARTICLES_DIR = os.path.join(BASE_DIR, "articles")
PILLOW_KB = 100  # covers below this size are Pillow fallbacks

REAL_PHOTO_RULES = (
    "IMPORTANT: This must look like a real photograph taken by a human photographer, not AI-generated art. "
    "Real skin texture with natural pores, subtle imperfections, no plastic or airbrushed look. "
    "Natural ambient light only — no studio lighting, no artificial rim light, no glowing backgrounds. "
    "Ordinary real-world setting, not a dramatic or fantasy landscape. "
    "Candid unposed body language — no model poses, no perfect symmetry, no forced expressions. "
    "No oversaturated colors, no HDR effect, no cinematic color grading. "
    "The photo must be indistinguishable from a real lifestyle photo shot by a real person."
)


def _openai_key():
    """Read OpenAI key fresh every call."""
    try:
        from config import OPENAI_API_KEY as key
    except Exception:
        key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        raise RuntimeError("OPENAI_API_KEY missing — cannot generate images")
    return key


def _openai_headers():
    return {
        "Authorization": f"Bearer {_openai_key()}",
        "Content-Type": "application/json",
    }


COVER_PROMPTS = {
    "Mental Wellness": (
        "Candid lifestyle photo: a young woman, late 20s, in a quiet home setting — "
        "bedroom, living room, or kitchen — in a calm intentional moment after managing stress. "
        "Natural body language, warm soft window light. Real skin, no perfection. "
        "Shot on 85mm f/1.8, shallow depth of field, warm tones. "
        "Photorealistic documentary wellness photography. No text, no logos, no watermarks."
    ),
    "Productivity": (
        "Candid lifestyle photo: a young woman, late 20s, at a clean minimal home desk, "
        "writing in a planner or looking at a laptop with calm focused expression. "
        "Natural window light, a plant nearby, warm neutral tones. Real skin. "
        "Shot on 85mm f/1.8, shallow depth of field. "
        "Photorealistic candid lifestyle photography. No text, no logos, no watermarks."
    ),
    "Healthy Lifestyle": (
        "Candid lifestyle photo: a young woman, late 20s, in a bright kitchen or nature setting, "
        "holding a warm mug or moving gently. Warm morning light, real skin, genuine expression. "
        "Shot on 85mm f/1.8, shallow depth of field, warm tones. "
        "Photorealistic candid wellness photography. No text, no logos, no watermarks."
    ),
}

SECTION_PROMPTS = {
    "Mental Wellness": [
        ("Candid photo: a young woman, early 30s, sitting on a sofa pressing one hand lightly "
         "to her chest, wide eyes showing early stress building. Real skin, natural light. "
         "Shot on 50mm f/2.0, warm tones. Photorealistic lifestyle. No text, no logos."),
        ("Candid photo: a young woman, late 20s, doing a breathing exercise — eyes closed, "
         "hands on knees, sitting cross-legged on a yoga mat. Soft natural light. "
         "Shot on 85mm f/1.8. Photorealistic wellness lifestyle. No text, no logos."),
        ("Morning lifestyle photo: a young woman, mid-20s, journaling at a kitchen table "
         "with a warm mug beside her. Calm focused expression, morning sunlight through window. "
         "Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos."),
    ],
    "Productivity": [
        ("Candid photo: a young woman, early 30s, at a desk staring at a laptop with a slightly "
         "overwhelmed expression. Real work stress, afternoon light. "
         "Shot on 50mm f/2.0. Photorealistic lifestyle. No text, no logos."),
        ("Candid photo: a young woman, late 20s, writing in a planner at a clean desk, "
         "calm and intentional. Morning light, plant nearby. "
         "Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos."),
        ("Lifestyle photo: a young woman, mid-20s, taking a break at her desk — arms stretched "
         "above her head, eyes closed, small relieved smile. Warm tones. "
         "Shot on 85mm f/1.8. Photorealistic candid. No text, no logos."),
    ],
    "Healthy Lifestyle": [
        ("Candid photo: a young woman, early 30s, preparing a healthy breakfast in a bright "
         "kitchen. Natural morning light, real skin, genuine moment. "
         "Shot on 50mm f/2.0. Photorealistic lifestyle. No text, no logos."),
        ("Lifestyle photo: a young woman, late 20s, walking on a quiet tree-lined path, "
         "calm and present. Dappled sunlight, warm tones. "
         "Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos."),
        ("Morning lifestyle photo: a young woman, mid-20s, sitting at a kitchen table with "
         "a warm mug, eyes soft and present. Warm morning light. "
         "Shot on 85mm f/1.8. Photorealistic lifestyle. No text, no logos."),
    ],
}


def generate_image(prompt, filename, fmt, max_kb):
    """Generate image via DALL-E 3 (synchronous — no polling needed)."""
    full_prompt = f"{prompt} {REAL_PHOTO_RULES}"
    body = {
        "model": "dall-e-3",
        "prompt": full_prompt,
        "size": "1792x1024",
        "quality": "standard",
        "style": "natural",
        "n": 1,
    }
    try:
        r = requests.post(
            "https://api.openai.com/v1/images/generations",
            json=body, headers=_openai_headers(), timeout=120
        )
    except Exception as e:
        print(f"    Request error: {e}")
        return False
    if r.status_code != 200:
        print(f"    API error {r.status_code}: {r.text[:200]}")
        return False
    image_url = r.json()["data"][0]["url"]
    img_resp = requests.get(image_url, timeout=60)
    if img_resp.status_code != 200:
        return False
    img = Image.open(io.BytesIO(img_resp.content)).convert("RGB")
    img = img.resize((1920, 1080), Image.LANCZOS)
    out_path = os.path.join(IMAGES_DIR, filename)
    if fmt == "JPEG":
        for q in range(88, 15, -4):
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=q, optimize=True)
            if buf.tell() / 1024 <= max_kb:
                break
    else:
        for q in range(92, 10, -5):
            buf = io.BytesIO()
            img.save(buf, format="WEBP", quality=q, method=4)
            if buf.tell() / 1024 <= max_kb:
                break
    with open(out_path, "wb") as f:
        f.write(buf.getvalue())
    print(f"    Saved {filename} ({os.path.getsize(out_path)//1024}KB)")
    return True


def inject_sections(slug, html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    if f"{slug}-sec1.webp" in html:
        return  # already injected
    h2s = list(re.finditer(r'<h2>[^<]+</h2>', html))
    if len(h2s) < 6:
        print(f"    WARNING: only {len(h2s)} h2s — skipping injection")
        return
    img_style = 'style="width:100%;border-radius:10px;margin:28px 0 20px;display:block;object-fit:cover;" loading="lazy"'
    injections = [
        (h2s[1].start(), f"{slug}-sec1.webp", "lifestyle wellness photo section 1"),
        (h2s[3].start(), f"{slug}-sec3.webp", "lifestyle wellness photo section 3"),
        (h2s[5].start(), f"{slug}-sec5.webp", "lifestyle wellness photo section 5"),
    ]
    for pos, fname, alt in reversed(injections):
        tag = f'\n      <img src="../images/{fname}" alt="{alt}" {img_style}>\n\n      '
        html = html[:pos] + tag + html[pos:]
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"    Section images injected into HTML")


def get_category(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    for cat in ["Mental Wellness", "Productivity", "Healthy Lifestyle"]:
        if cat in content:
            return cat
    return "Mental Wellness"


def main():
    html_files = sorted(f for f in os.listdir(ARTICLES_DIR) if f.endswith(".html"))
    needs_fix = []

    for html_file in html_files:
        slug = html_file[:-5]
        cover = os.path.join(IMAGES_DIR, f"{slug}.jpg")
        sec1  = os.path.join(IMAGES_DIR, f"{slug}-sec1.webp")
        if not os.path.exists(cover):
            continue
        cover_kb  = os.path.getsize(cover) / 1024
        bad_cover = cover_kb < PILLOW_KB
        no_secs   = not os.path.exists(sec1)
        if bad_cover or no_secs:
            needs_fix.append((slug, html_file, bad_cover, no_secs, cover_kb))

    if not needs_fix:
        print("All articles OK — no Pillow fallbacks detected.")
        return

    print(f"\n{len(needs_fix)} article(s) need fixing:\n")
    fixed = 0
    for slug, html_file, bad_cover, no_secs, cover_kb in needs_fix:
        html_path = os.path.join(ARTICLES_DIR, html_file)
        category  = get_category(html_path)
        issues    = []
        if bad_cover: issues.append(f"Pillow cover ({cover_kb:.0f}KB)")
        if no_secs:   issues.append("missing section images")
        print(f"  {slug} — {', '.join(issues)}")

        ok = True
        if bad_cover:
            prompt = COVER_PROMPTS.get(category, COVER_PROMPTS["Mental Wellness"])
            if not generate_image(prompt, f"{slug}.jpg", "JPEG", 250):
                print(f"    Cover generation failed — skipping")
                ok = False

        if no_secs and ok:
            sec_prompts = SECTION_PROMPTS.get(category, SECTION_PROMPTS["Mental Wellness"])
            sec_ok = 0
            for i, prompt in enumerate(sec_prompts):
                idx = [1, 3, 5][i]
                if generate_image(prompt, f"{slug}-sec{idx}.webp", "WEBP", 500):
                    sec_ok += 1
            if sec_ok == 3:
                inject_sections(slug, html_path)
            else:
                print(f"    Only {sec_ok}/3 section images generated")
                ok = False

        if ok:
            fixed += 1
            if needs_fix.index((slug, html_file, bad_cover, no_secs, cover_kb)) < len(needs_fix) - 1:
                time.sleep(15)  # avoid Leonardo rate limit between articles

    print(f"\nauto_fix_covers: {fixed}/{len(needs_fix)} articles fixed.")


if __name__ == "__main__":
    main()
