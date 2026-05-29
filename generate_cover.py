"""
NicheHubPro — Cover Image Generator
Uses HF FLUX.1-schnell for all image generation.
Falls back to branded Pillow cover on error.

Usage:
  python generate_cover.py "how to stop overthinking at night" "Mental Wellness"
  python generate_cover.py --batch
"""

import sys, os, re, io, time, requests, urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image, ImageDraw, ImageFont

OUT_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")

REAL_PHOTO_RULES = (
    "HUMANIZATION RULES — apply every single one: "
    "This must look like a real unedited snapshot taken on a smartphone by a friend — NOT AI art, NOT stock photo, NOT professional shoot. "
    "Skin: visible pores, subtle blemishes, natural redness on cheeks or nose, slight unevenness in skin tone — ZERO smooth AI skin, ZERO glowing or poreless complexion. "
    "Eyes: asymmetric, slightly tired or watery, natural catchlights only — NOT perfectly symmetrical, NOT AI-sharp. "
    "Hair: messy real texture with flyaways, frizz, split ends, baby hairs — NOT perfectly styled, NOT shiny or glossy. "
    "Face: candid, absorbed, or slightly tired expression — NOT a posed smile, NOT a model face, NOT direct eye contact with camera. "
    "A small real-life imperfection is required: a small blemish, under-eye shadow, slight asymmetry, or redness — NEVER a perfect face. "
    "Clothing: visibly faded, slightly wrinkled, ordinary everyday fabric — old hoodie, plain t-shirt, basic knit — NEVER stylish, tailored, or flattering. "
    "Frame: shoulders or collarbone up only — never show chest or body below. "
    "Lighting: flat natural window light or overcast daylight — NO studio rim light, NO beauty dish, NO glowing halo. "
    "Background: plain and slightly cluttered — bare wall, basic kitchen, ordinary desk — NO styled props, NO magazines staging. "
    "Composition: slightly off-center, imperfect handheld framing — NOT centered, NOT symmetrical. "
    "NO oversaturation, NO HDR, NO color grading, NO vignette, NO filters. "
    "Photographic grain is acceptable and preferred over AI-smooth output."
)

NEGATIVE_PROMPT = (
    "artificial skin, plastic skin, porcelain skin, glowing skin, perfect skin, doll face, "
    "AI generated look, digital art, illustration, painting, CGI render, stock photo, "
    "model pose, beauty campaign, magazine cover, symmetrical face, flawless complexion, "
    "studio lighting, rim lighting, beauty dish, smooth skin, airbrushed, retouched, "
    "watermark, text, logo, signature, blurry face, anime, cartoon, drawing, "
    "extra fingers, missing fingers, six fingers, four fingers, malformed hands, "
    "extra hands, three hands, fused fingers, distorted hands, deformed fingers, "
    "extra limbs, extra arms, floating hands, unnatural hands, bad anatomy"
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
W, H      = 800, 450
MAX_KB    = 80

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

# ── AI IMAGE GENERATION — HF FLUX.1-dev ──────────────────────────────────
_HF_API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-dev"

def generate_with_ai(topic, category, custom_prompt=None, retries=3, candidates=3):
    """
    Generate cover image via HF FLUX.1-dev at 1024x576.
    Generates `candidates` versions, keeps the one with most unique colors (most photorealistic).
    """
    try:
        from config import HF_API_KEY
    except ImportError:
        HF_API_KEY = os.environ.get("HF_API_KEY", "")

    prompt = build_image_prompt(topic, category, custom_prompt)
    full_prompt = f"{prompt} {REAL_PHOTO_RULES}"

    best_img    = None
    best_unique = 0

    for attempt in range(1, candidates + 1):
        try:
            print(f"  HF FLUX.1-dev attempt {attempt}/{candidates}...")
            resp = requests.post(
                _HF_API_URL,
                headers={"Authorization": f"Bearer {HF_API_KEY}"},
                json={"inputs": full_prompt, "parameters": {"width": 1024, "height": 576}},
                verify=False,
                timeout=180,
            )
            resp.raise_for_status()
            img = Image.open(io.BytesIO(resp.content)).convert("RGB")
            img = img.resize((W, H), Image.LANCZOS)

            # Pick candidate with most unique colors — highest = most photorealistic
            small = img.resize((100, 56))
            data  = small.tobytes()
            unique = len(set(data[i:i+3] for i in range(0, len(data), 3)))
            print(f"    Candidate {attempt}: {len(resp.content)//1024}KB, {unique} unique colors", end="")

            if unique > best_unique:
                best_img    = img
                best_unique = unique
                print(" — best so far")
            else:
                print(" — keeping previous")

            if attempt < candidates:
                time.sleep(10)

        except Exception as e:
            print(f"    Error: {e}")
            if attempt < candidates:
                time.sleep(10)

    if best_img:
        print(f"  Selected best candidate: {best_unique} unique colors")
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
