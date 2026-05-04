"""
NicheHubPro — Cover Image Generator
Uses HF FLUX.1-schnell for all image generation.
Falls back to branded Pillow cover on error.

Usage:
  python generate_cover.py "how to stop overthinking at night" "Mental Wellness"
  python generate_cover.py --batch
"""

import sys, os, re, io, time, requests
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image, ImageDraw, ImageFont

OUT_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")

REAL_PHOTO_RULES = (
    "CRITICAL RULES — strictly follow all of these: "
    "Frame the shot from the shoulders or collarbone UP only — never show chest or body below shoulders. "
    "MUST look like a real unedited photo taken on a phone by a friend — NOT AI art, NOT a stock photo, NOT professional photography. "
    "Skin: visible pores, mild under-eye shadows, natural redness, slight skin texture unevenness — absolutely NO smooth AI skin, NO glowing skin, NO perfect complexion. "
    "Hair: real texture with flyaways, frizz, or baby hairs — NOT perfectly styled or shiny. "
    "Face: genuine candid expression — slightly distracted, absorbed, or tired — NEVER a posed smile, NEVER a model expression, NEVER direct eye contact with camera. "
    "Clothing: visibly faded, slightly wrinkled, ordinary — old hoodie, plain t-shirt, basic sweatshirt — NEVER stylish, fitted, or flattering. "
    "Lighting: flat natural window light or overcast daylight — NO studio lights, NO rim light, NO beauty dish, NO glowing halo around subject. "
    "Background: ordinary and slightly messy — cluttered desk, plain wall, basic kitchen — NO magazine staging, NO aesthetic props. "
    "Composition: slightly off-center, imperfect framing, as if handheld — NOT perfectly centered, NOT symmetrical. "
    "NO oversaturation, NO HDR, NO cinematic color grading, NO vignette. "
    "If the result looks like a stock photo, AI image, or beauty campaign — it is WRONG. Regenerate with more imperfections."
)
# Font paths — Windows first, Linux fallback
def _find_font(win_path, linux_names):
    if os.path.exists(win_path):
        return win_path
    for name in linux_names:
        for d in ["/usr/share/fonts", "/usr/local/share/fonts", "/usr/share/fonts/truetype"]:
            for root, _, files in os.walk(d):
                if name in files:
                    return os.path.join(root, name)
    return None

FONT_BOLD = _find_font("c:/Windows/Fonts/arialbd.ttf", ["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"])
FONT_REG  = _find_font("c:/Windows/Fonts/arial.ttf",   ["DejaVuSans.ttf",      "LiberationSans-Regular.ttf"])
W, H      = 1920, 1080
MAX_KB    = 250

# ── BRAND COLORS (fallback) ───────────────────────────────────────────────
DARK1  = (30,  42,  47)
DARK2  = (20,  55,  45)
GREEN  = (107, 175, 146)
WHITE  = (255, 255, 255)

CATEGORY_SCENES = {
    "Mental Wellness":   {
        "emotion": "stress, anxiety or overthinking, with a subtle expression of seeking peace",
        "setting": "quiet bedroom or softly lit living room with plants and natural textures",
        "action":  "sitting on a bed or floor, eyes closed or looking out the window"
    },
    "Productivity":      {
        "emotion": "quiet focus and calm determination",
        "setting": "clean minimal home office, wooden desk, one plant, natural light",
        "action":  "writing in a journal or looking at a laptop with a focused expression"
    },
    "Healthy Lifestyle": {
        "emotion": "peaceful energy and physical wellbeing",
        "setting": "bright morning kitchen, outdoor nature path, or yoga space",
        "action":  "preparing a healthy drink, walking barefoot, or stretching gently"
    },
}

# ── SLUG ──────────────────────────────────────────────────────────────────
def slug(title):
    s = title.lower()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'\s+', '-', s.strip())
    s = re.sub(r'-+', '-', s)
    return s[:60]

# ── BUILD IMAGE PROMPT ────────────────────────────────────────────────────
def build_image_prompt(topic, category, custom_prompt=None):
    """
    Build the FLUX prompt using the new detailed cover image template.
    Uses Claude-generated custom_prompt if available, otherwise builds from template.
    """
    strict_rules = (
        "STRICT RULES: no text, no logos, no watermark, no over-editing, "
        "do not make it look like a stock photo, each image must be unique. "
        "No text, no words, no graphic overlays anywhere. "
        "Output: 4K ultra realistic natural colors."
    )

    if custom_prompt and len(custom_prompt) > 30:
        prompt = f"{custom_prompt}. {strict_rules}"
    else:
        scene = CATEGORY_SCENES.get(category, CATEGORY_SCENES["Mental Wellness"])
        prompt = (
            f"Photorealistic wellness lifestyle photo for an article about: {topic}. "
            f"Scene: a calm, modern, real-life environment reflecting mental wellness. "
            f"Subject: a young woman (25-35 years old) expressing {scene['emotion']} with natural unposed body language. "
            f"Details: {scene['action']}, authentic everyday setting, minimal clean background, "
            f"soft textures like bed sheets, desk, plants, natural light. "
            f"Lighting: soft natural morning sunlight or dim evening light, warm calming tones (green, beige, soft blue). "
            f"Style: photorealistic, minimalist wellness aesthetic, depth of field, slightly blurred background, "
            f"shot like a real camera, not AI look. "
            f"Mood: emotional but peaceful, relatable and human. "
            f"Composition: subject slightly off-center, focus on emotion not perfection. "
            f"{strict_rules}"
        )
    return f"{prompt} {REAL_PHOTO_RULES}"

# ── COMPRESS IMAGE ────────────────────────────────────────────────────────
def compress_to_limit(img, max_kb=MAX_KB):
    if img.size != (W, H):
        img = img.resize((W, H), Image.LANCZOS)
    for quality in range(88, 15, -3):
        buf = io.BytesIO()
        img.convert('RGB').save(buf, format='JPEG', quality=quality, optimize=True)
        size_kb = buf.tell() / 1024
        if size_kb <= max_kb:
            return buf.getvalue(), quality, size_kb
    buf = io.BytesIO()
    img.convert('RGB').save(buf, format='JPEG', quality=20, optimize=True)
    return buf.getvalue(), 20, buf.tell() / 1024

# ── AI IMAGE GENERATION — HF FLUX.1-schnell ──────────────────────────────
MIN_QUALITY_KB = 100  # Images under this size are likely flat/AI-looking — reject and retry

def generate_with_ai(topic, category, custom_prompt=None, retries=3, candidates=2):
    """
    Generate cover image via HF FLUX.1-schnell.
    Generates `candidates` versions, keeps the largest (most detail = least AI-looking).
    Retries automatically if image is under MIN_QUALITY_KB.
    """
    from huggingface_hub import InferenceClient
    try:
        from config import HF_API_KEY
    except ImportError:
        HF_API_KEY = os.environ.get("HF_API_KEY", "")

    rules = (
        "Editorial photograph. "
        "Head-and-shoulders crop only, chest not visible. "
        "Real human face and skin: visible pores, natural imperfections, genuine hair texture, "
        "authentic non-posed expression — not AI-smooth, not a model. "
        "Plain everyday clothing. "
        "Shot on Sony A7IV 85mm f/1.8, shallow depth of field, slightly blurred background. "
        "Sharp focus, 4K photorealistic. "
        "Single photograph only, not a diptych or collage. No text, no logos, no watermarks."
    )
    prompt = build_image_prompt(topic, category, custom_prompt)
    full_prompt = f"{prompt} {rules}"
    client = InferenceClient(provider="hf-inference", api_key=HF_API_KEY)

    best_img  = None
    best_size = 0

    for attempt in range(1, retries + 1):
        try:
            print(f"  HF FLUX attempt {attempt}/{retries}...")
            result = client.text_to_image(
                model="black-forest-labs/FLUX.1-schnell",
                prompt=full_prompt,
                width=1280, height=720,
            )
            img = result if isinstance(result, Image.Image) else Image.open(io.BytesIO(result))
            img = img.resize((W, H), Image.LANCZOS)

            # Measure size in memory to assess quality
            buf = io.BytesIO()
            img.convert("RGB").save(buf, format="JPEG", quality=85)
            size_kb = buf.tell() / 1024

            print(f"    Candidate {attempt}: {size_kb:.0f}KB", end="")

            if size_kb < MIN_QUALITY_KB:
                print(f" — too small (likely flat/AI), retrying...")
                time.sleep(8)
                continue

            print(f" — {'best so far' if size_kb > best_size else 'keeping previous'}")
            if size_kb > best_size:
                best_img  = img
                best_size = size_kb

            # If we have enough good candidates, stop early
            if attempt >= candidates and best_img is not None:
                break

            if attempt < retries:
                time.sleep(8)

        except Exception as e:
            print(f"  Error: {e}")
            if attempt < retries:
                time.sleep(8)

    if best_img:
        print(f"  Selected best candidate: {best_size:.0f}KB")
    return best_img

# ── PILLOW FALLBACK ───────────────────────────────────────────────────────
def generate_pillow_cover(title, category):
    img = Image.new('RGB', (W, H), DARK1)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(DARK1[0] + (DARK2[0] - DARK1[0]) * t)
        g = int(DARK1[1] + (DARK2[1] - DARK1[1]) * t)
        b = int(DARK1[2] + (DARK2[2] - DARK1[2]) * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for i in range(40):
        t = i / 40
        r = int(380 * (1 - t))
        a = int(50 * (1 - t) ** 2)
        od.ellipse([int(W*0.75)-r, int(H*0.25)-r, int(W*0.75)+r, int(H*0.25)+r],
                   fill=(GREEN[0], GREEN[1], GREEN[2], a))
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 4], fill=GREEN)

    try:
        font_t = ImageFont.truetype(FONT_BOLD, 58 if len(title) <= 50 else 46)
        font_c = ImageFont.truetype(FONT_BOLD, 22)
        font_b = ImageFont.truetype(FONT_BOLD, 20)
        font_u = ImageFont.truetype(FONT_REG,  18)
    except Exception:
        font_t = font_c = font_b = font_u = ImageFont.load_default()

    cat_text = category.upper()
    bx, by = 60, 52
    bb = draw.textbbox((0,0), cat_text, font=font_c)
    bw, bh = bb[2]-bb[0]+36, bb[3]-bb[1]+18
    bi = Image.new('RGBA', (W,H), (0,0,0,0))
    bd = ImageDraw.Draw(bi)
    bd.rounded_rectangle([bx, by, bx+bw, by+bh], radius=bh//2,
                         fill=(107,175,146,40), outline=(107,175,146,120), width=1)
    img = Image.alpha_composite(img.convert('RGBA'), bi).convert('RGB')
    draw = ImageDraw.Draw(img)
    draw.text((bx+18, by+9), cat_text, font=font_c, fill=GREEN)

    words, lines, current = title.split(), [], []
    for word in words:
        test = ' '.join(current + [word])
        if draw.textbbox((0,0), test, font=font_t)[2] > W-120 and current:
            lines.append(' '.join(current)); current = [word]
        else:
            current.append(word)
    if current: lines.append(' '.join(current))
    lh = draw.textbbox((0,0),"Ag",font=font_t)[3] + 14
    ty = 160
    for line in lines:
        draw.text((60, ty), line, font=font_t, fill=WHITE); ty += lh
    draw.rectangle([60, ty+14, 124, ty+18], fill=GREEN)
    draw.text((60, H-58), "NicheHubPro", font=font_b, fill=WHITE)
    draw.text((60+134, H-57), "nichehubpro.com", font=font_u, fill=GREEN)
    return img

# ── MAIN FUNCTION ─────────────────────────────────────────────────────────
def generate_cover(title, category="Mental Wellness",
                   output_path=None, custom_prompt=None):
    os.makedirs(OUT_DIR, exist_ok=True)

    if output_path is None:
        output_path = os.path.join(OUT_DIR, slug(title) + ".jpg")

    # Try AI generation first, fall back to Pillow
    img = generate_with_ai(title, category, custom_prompt)
    if img is None:
        print("  Falling back to Pillow cover...")
        img = generate_pillow_cover(title, category)

    # Compress to <100kb
    data, quality, size_kb = compress_to_limit(img)
    with open(output_path, 'wb') as f:
        f.write(data)

    print(f"  Saved: {os.path.basename(output_path)} ({size_kb:.1f}kb)")
    return output_path


# ── BATCH LIST ────────────────────────────────────────────────────────────
ARTICLES = [
    ("how to stop overthinking at night",    "Mental Wellness"),
    ("how to calm anxiety quickly",           "Mental Wellness"),
    ("signs of mental exhaustion",            "Mental Wellness"),
    ("how to reduce stress naturally",        "Mental Wellness"),
    ("how to stop negative thoughts",         "Mental Wellness"),
    ("how to relax your mind",                "Mental Wellness"),
    ("how to deal with anxiety daily",        "Mental Wellness"),
    ("how to focus without distractions",     "Productivity"),
    ("how to stop procrastination",           "Productivity"),
    ("simple daily routine for productivity", "Productivity"),
    ("how to stay motivated daily",           "Productivity"),
    ("how to avoid burnout at work",          "Mental Wellness"),
    ("how to manage time better",             "Productivity"),
    ("how to build discipline",               "Productivity"),
    ("morning routine for mental health",     "Healthy Lifestyle"),
    ("how to sleep better naturally",         "Healthy Lifestyle"),
    ("foods that reduce anxiety",             "Healthy Lifestyle"),
    ("how to increase energy naturally",      "Healthy Lifestyle"),
    ("benefits of walking daily",             "Healthy Lifestyle"),
    ("how to detox your mind",                "Mental Wellness"),
    ("habits for a healthy lifestyle",        "Healthy Lifestyle"),
    ("signs of anxiety disorder",             "Mental Wellness"),
    ("how to stop panic attacks",             "Mental Wellness"),
    ("how to build confidence",               "Mental Wellness"),
    ("how to stop worrying",                  "Mental Wellness"),
    ("how to improve mental clarity",         "Mental Wellness"),
    ("how to feel happy again",               "Mental Wellness"),
    ("how to reset your life",                "Mental Wellness"),
    ("how to change your habits",             "Productivity"),
    ("how to improve your life",              "Mental Wellness"),
]


def main():
    args = sys.argv[1:]
    if '--batch' in args:
        print(f"Generating {len(ARTICLES)} AI covers...\n")
        for i, (title, category) in enumerate(ARTICLES, 1):
            print(f"\n[{i:02d}/{len(ARTICLES)}] {title}")
            generate_cover(title, category)
            time.sleep(2)  # be polite to the API
        print(f"\nDone. Saved to: {OUT_DIR}")
    elif len(args) >= 1:
        generate_cover(args[0], args[1] if len(args) >= 2 else "Mental Wellness")
    else:
        print("Generating demo cover...")
        generate_cover("how to stop overthinking at night", "Mental Wellness")
        print(f'\nUsage:')
        print(f'  python generate_cover.py "Title" "Mental Wellness"')
        print(f'  python generate_cover.py --batch')


if __name__ == "__main__":
    main()
