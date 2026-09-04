"""
NicheHubPro — Cover Image Generator
Uses HF FLUX.1-schnell for all image generation.
Generation fails closed when a compliant image cannot be created.

Usage:
  python generate_cover.py "how to stop overthinking at night" "Mental Wellness"
  python generate_cover.py --batch
"""

import sys, os, re, io, time, requests, urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image

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
W, H      = 800, 450
MAX_KB    = 80

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
    "Healthy Lifestyle - Food": {
        "emotion": "nourishment, calm energy and genuine enjoyment of healthy food",
        "setting": "bright clean kitchen counter or wooden table with soft natural window light",
        "action":  "holding a bowl of colorful food or a glass of juice with both hands, taking a bite, chopping vegetables, or preparing a healthy meal — person is always present and central"
    },
}

_FOOD_KEYWORDS = [
    'food', 'eat', 'eating', 'meal', 'diet', 'nutrition', 'snack', 'breakfast',
    'protein', 'vegetable', 'fruit', 'water', 'drink', 'juice', 'smoothie',
    'recipe', 'cook', 'sugar', 'vitamin', 'supplement', 'anti-inflammatory',
    'calorie', 'fiber', 'hydrat', 'ingredient', 'salad', 'plant-based',
    'carb', 'fat', 'gut', 'digestion', 'probiotic', 'caffeine', 'coffee',
]

def _is_food_topic(topic):
    t = topic.lower()
    return any(kw in t for kw in _FOOD_KEYWORDS)

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
        # Use food-specific scene for Healthy Lifestyle food/drink articles
        if category == "Healthy Lifestyle" and _is_food_topic(topic):
            scene = CATEGORY_SCENES["Healthy Lifestyle - Food"]
            prompt = (
                f"Candid lifestyle photo for an article about: {topic}. "
                f"Subject: a real young woman (25-35), {scene['action']}. "
                f"Setting: {scene['setting']}. "
                f"Emotion: {scene['emotion']} — genuine candid expression, not posed. "
                f"Skin: real skin texture, visible pores, natural imperfections — absolutely no AI-smooth skin. "
                f"Hair: slightly messy, real texture with flyaways. "
                f"Clothing: plain everyday fabric — t-shirt, linen top, basic knit — never stylish or fitted. "
                f"Lighting: soft natural window light, warm tones, no studio lighting. "
                f"Style: photorealistic, shallow depth of field, slightly blurred background, shot like a real camera. "
                f"Composition: slightly off-center, human and relatable, not a stock photo. "
                f"{strict_rules}"
            )
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

# ── AI IMAGE GENERATION — HF fal-ai FLUX.1-dev ───────────────────────────
_HF_API_URL = "https://router.huggingface.co/fal-ai/fal-ai/flux/dev"

def generate_with_ai(topic, category, custom_prompt=None, retries=3, candidates=1):
    """
    Generate cover image via HuggingFace (fal-ai FLUX.1-dev) at 1024x576.
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
                json={
                    "prompt": full_prompt,
                    "negative_prompt": NEGATIVE_PROMPT,
                    "image_size": {"width": 1024, "height": 576},
                    "num_inference_steps": 50,
                    "guidance_scale": 3.5,
                    "num_images": 1,
                    "seed": attempt * 42,
                },
                verify=False,
                timeout=90,
            )
            resp.raise_for_status()
            data = resp.json()
            img_url = data["images"][0]["url"]
            img_resp = requests.get(img_url, verify=False, timeout=45)
            img_resp.raise_for_status()
            img = Image.open(io.BytesIO(img_resp.content)).convert("RGB")
            img = img.resize((W, H), Image.LANCZOS)

            small = img.resize((100, 56))
            px    = small.tobytes()
            unique = len(set(px[i:i+3] for i in range(0, len(px), 3)))
            print(f"    Candidate {attempt}: {len(img_resp.content)//1024}KB, {unique} unique colors", end="")

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

# ── MAIN FUNCTION ─────────────────────────────────────────────────────────
def generate_cover(title, category="Mental Wellness",
                   output_path=None, custom_prompt=None):
    os.makedirs(OUT_DIR, exist_ok=True)

    if output_path is None:
        output_path = os.path.join(OUT_DIR, slug(title) + ".jpg")

    # Never fall back to a branded graphic: article imagery must never contain
    # text, logos, signatures, or watermarks.
    img = generate_with_ai(title, category, custom_prompt)
    if img is None:
        raise RuntimeError(
            "Cover generation failed. No image was saved because a professional "
            "cover must be a text-free, logo-free, watermark-free photograph."
        )

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
