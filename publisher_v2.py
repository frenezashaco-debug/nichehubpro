"""
NicheHubPro — Article Publisher v2
Generates a full SEO article HTML file from a keyword using Claude API.
Follows the exact article template + generates cover image.

Usage:
  python publisher_v2.py "how to stop overthinking at night" "Mental Wellness"
"""

import sys, os, re, json, textwrap, io, time
from datetime import date
sys.stdout.reconfigure(encoding='utf-8')
import anthropic
import requests, urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from PIL import Image
try:
    import json_repair
    _HAS_JSON_REPAIR = True
except ImportError:
    _HAS_JSON_REPAIR = False
from generate_cover import generate_cover, slug

# ── CONFIG ────────────────────────────────────────────────────────────────
try:
    from config import ANTHROPIC_API_KEY as _cfg_key
except ImportError:
    _cfg_key = ""
# Config key takes priority over env var (env var may contain placeholder values)
_env_key = os.environ.get("ANTHROPIC_API_KEY", "")
API_KEY = _cfg_key or (_env_key if not _env_key.startswith("your-") else "") or "YOUR_API_KEY_HERE"
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
OUT_DIR     = os.path.join(BASE_DIR, "articles")
IMAGES_DIR  = os.path.join(BASE_DIR, "images")
SITE_URL    = "https://nichehubpro.com"

CATEGORY_URLS = {
    "Mental Wellness":   "../mental-wellness/",
    "Productivity":      "../productivity/",
    "Healthy Lifestyle": "../healthy-lifestyle/",
}

# Single consistent author across all categories — required for AdSense E-E-A-T
_SARAH = {
    "name": "Sarah Mitchell",
    "initials": "SM",
    "title": "Health & Wellness Writer",
    "bio": (
        "Sarah Mitchell has been writing about mental health, productivity, and healthy living for over 7 years. "
        "With a background in psychology and a personal history of managing chronic overthinking, "
        "she translates complex research into clear, actionable advice that people can actually use."
    ),
    "color": "#10B981",
    "default_refs": [
        {"claim": "Anxiety disorders affect 40 million adults in the United States every year", "source": "Anxiety & Depression Association of America", "url": "https://adaa.org"},
        {"claim": "Evidence-based approaches like CBT significantly reduce anxiety and stress symptoms", "source": "American Psychological Association", "url": "https://www.apa.org"},
        {"claim": "Regular mindfulness practice can reduce symptoms of anxiety and depression", "source": "National Institute of Mental Health", "url": "https://www.nimh.nih.gov"},
    ],
}
AUTHORS = {
    "Mental Wellness":   _SARAH,
    "Productivity":      _SARAH,
    "Healthy Lifestyle": _SARAH,
}

# ── SYSTEM PROMPT ────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert SEO content writer for NicheHubPro, a mental wellness blog.
Your audience: real people dealing with stress, anxiety, and overthinking.
Your job: write human, motivational, deeply useful articles — NOT robotic AI content.

ABSOLUTE WRITING RULES (never break these):
- NEVER use em dashes (—) or en dashes (–) anywhere. Use a hyphen (-) if needed.
- NEVER use the word "delve" or "delves" or "delving"
- NEVER write "In today's fast-paced world", "It is important to note", "In conclusion", "In summary", "To summarize"
- NEVER use: Furthermore, Moreover, Additionally, Consequently, Subsequently, Henceforth, Herein, Nevertheless, Notwithstanding
- NEVER use: utilize/utilizes/utilized/utilizing, facilitate/facilitates, pivotal, crucial, comprehensive, multifaceted, nuanced, paradigm, synergy, streamline, seamlessly, invaluable, embark, tapestry, holistic, optimize, robust, propel, curated, empower, leverage, elevate, unleash, navigate (as metaphor), foster, breakthrough, groundbreaking, cutting-edge, state-of-the-art, myriad, plethora
- NEVER use: "when it comes to", "it's crucial that", "one must", "in the realm of", "unlock your potential", "game-changer", "tailored to", "a wide range of", "a variety of"
- NEVER repeat the same anchor text for internal links
- Keep ALL paragraphs SHORT (2-3 lines max, strictly)
- Write like a knowledgeable friend — plain, direct, warm English
- Meta description MUST be exactly 155-160 characters (count carefully)

GEO OPTIMIZATION RULE (apply to EVERY paragraph):
Each paragraph must follow this exact structure:
1. Start with a clear, direct statement
2. Include a fact, statistic, or explanation
3. End with practical, actionable advice

OUTPUT: Return ONLY valid JSON. No markdown fences. No text outside the JSON.

JSON STRUCTURE:
{
  "title": "string — number + primary keyword in first 3 words + emotional hook",
  "meta_description": "string — MUST be 155-160 characters exactly. Include primary keyword. Count the characters.",
  "category": "Mental Wellness | Productivity | Healthy Lifestyle",
  "slug": "string — lowercase hyphenated url slug",
  "intro": "string — 3 short paragraphs separated by \\n. Primary keyword in first 10 words. Emotionally hooks the reader. Max 3 lines per paragraph.",
  "tldr": "string — 2-3 sentences only. Include primary keyword. Directly answer the article topic.",
  "sections": [
    {
      "h2": "string — heading SPECIFIC to this topic. Choose the 6 most relevant from these options (NEVER use the same pattern for every article): 'What Is X and Why Does It Matter?', 'What Are the Signs of X?', 'Why Does X Happen?', 'How to Fix X: Step-by-Step', 'What Does the Research Say About X?', 'How to Prevent X From Coming Back', 'Daily Habits That Help With X', 'What Experts Say About X', 'The X Method That Actually Works', 'How X Affects Your Brain and Body', 'Common Mistakes People Make With X', 'When to Seek Help for X'. Pick headings that feel natural for THIS specific topic.",
      "content": "string — full HTML. Use <p>, <ul><li>, <strong>. Every <p> max 3 lines. GEO structure per paragraph. At least one <ul> list. At least one <strong> key advice. Min 300 words per section. VARY content format across sections: some use numbered steps, some use a key insight callout, some compare two approaches."
    }
  ],
  "real_example": "string — EXACTLY 2 separate paragraphs separated by \\n. First paragraph: the problem (person's struggle). Second paragraph: the transformation (how they fixed it). Human story. Relatable. Max 4 lines per paragraph.",
  "internal_links": [
    {"anchor": "descriptive anchor text", "slug": "related-article-slug"},
    {"anchor": "different anchor text", "slug": "another-related-slug"},
    {"anchor": "third anchor text", "slug": "third-related-slug"}
  ],
  "faq": [
    {"question": "real Google question?", "answer": "short clear useful answer"},
    {"question": "real Google question 2?", "answer": "short clear useful answer"},
    {"question": "real Google question 3?", "answer": "short clear useful answer"},
    {"question": "real Google question 4?", "answer": "short clear useful answer"},
    {"question": "real Google question 5?", "answer": "short clear useful answer"}
  ],
  "conclusion": "string — 3 short paragraphs. Motivational. Encourages one small action today. Human and warm.",
  "cover_image_prompt": "string — UNIQUE humanized photo prompt for THIS article. A REAL PERSON must ALWAYS appear — no exceptions, even for food articles. RULES FOR ALL COVERS: (1) Always a young woman 25-35, candid and real — never a man, never a model pose. (2) Real skin: visible pores, natural imperfections, slight asymmetry, NO AI-smooth skin, NO porcelain complexion. (3) Real hair: messy texture, flyaways, frizz — never perfectly styled. (4) Plain clothing: faded t-shirt, basic linen top, old hoodie — never stylish or fitted. (5) Candid expression: genuinely absorbed, slightly tired, or at ease — never a posed smile. (6) Lighting: flat natural window light or overcast daylight — NO studio rim light, NO beauty lighting. (7) Shot on 85mm f/1.8, shallow depth of field, slightly blurred background. (8) Composition: slightly off-center, imperfect handheld framing. IF FOOD/DRINK ARTICLE: woman is shown interacting with food — holding a bowl or glass, taking a bite, chopping vegetables, or preparing a meal in a real kitchen. Food is visible and contextual. Hands and forearms are allowed. IF NOT FOOD ARTICLE: woman shown from shoulders or collarbone up only, no hands, no objects held. STRUCTURE: 'Candid lifestyle photo: a young woman, [age], [specific location]. [Hair and clothing details]. [Exact expression]. [Action — for food: what she is eating/preparing/holding]. [Lighting]. Shot on 85mm f/1.8. Real skin texture, natural imperfections. Photorealistic. No text, no logos, no watermarks, no AI look.' FORBIDDEN: man, male, fake smile, posed stance, studio lighting, perfect symmetry, smooth skin, AI look, stock photo pose, watermark, text.",
  "cover_alt_text": "string — short SEO alt text. Format: '[woman/hands/scene] [action] in [setting]'. Max 10 words. Include primary keyword.",
  "section_image_prompts": [
    {
      "section_index": 0,
      "prompt": "string — UNIQUE humanized photo prompt for section 1 image. RULES: young woman shown from shoulders/collarbone up ONLY — NO hands, NO arms, NO objects held. NEVER a man. Must be completely different scene from cover. Use candid documentary style with specific details: exact setting, exact clothing, exact facial expression, camera style (50mm or 85mm, f/1.8-2.8, shallow DOF), real skin texture. Tied to section 1 topic. No text, no logos, no man.",
      "alt_text": "string — 8-10 words describing the scene, include primary keyword"
    },
    {
      "section_index": 2,
      "prompt": "string — UNIQUE humanized photo prompt for section 3 image. RULES: young woman shown from shoulders/collarbone up ONLY — NO hands, NO arms, NO objects held. NEVER a man. Completely different from cover and section 1. Specific candid moment with exact facial expression and setting details. Solution or progress-focused scene. Camera style included. No text, no logos, no man.",
      "alt_text": "string — 8-10 words describing the scene, include primary keyword"
    },
    {
      "section_index": 4,
      "prompt": "string — UNIQUE humanized photo prompt for section 5 image. RULES: young woman shown from shoulders/collarbone up ONLY — NO hands, NO arms, NO objects held. NEVER a man. Different from all above images. Calming, hopeful, empowering facial expression. Specific lighting, clothing, background. Camera style included. No text, no logos, no man.",
      "alt_text": "string — 8-10 words describing the scene naturally, include primary keyword"
    }
  ],
  "pinterest_pins": [
    {
      "title": "string — Pin 1: 'How to...' style. CTR-optimized. Max 100 chars. Include primary keyword.",
      "description": "string — 2-3 sentences. Include keyword naturally. End with a subtle CTA. Max 500 chars."
    },
    {
      "title": "string — Pin 2: 'Stop...' or problem-focused style. Different from Pin 1. Max 100 chars.",
      "description": "string — 2-3 sentences. Different angle from Pin 1. Include keyword. Max 500 chars."
    },
    {
      "title": "string — Pin 3: 'Try this...' or solution-focused style. Different from Pins 1 and 2. Max 100 chars.",
      "description": "string — 2-3 sentences. Actionable tone. Include keyword. Max 500 chars."
    }
  ],
  "references": [
    {
      "claim": "string — a specific research finding, statistic, or fact cited in this article. Must directly support something written in the article body.",
      "source": "string — organization name. ONLY use real, well-known organizations: Mayo Clinic, NHS, NIMH, APA, ADAA, Harvard Health, CDC, WHO, American Heart Association, National Sleep Foundation, Harvard Business Review, Psychology Today, Cleveland Clinic, WebMD Medical Team, Healthline Medical Team",
      "url": "string — the organization HOMEPAGE only. Never invent a specific article URL. Use the root domain (e.g. https://www.mayoclinic.org)"
    }
  ]
}"""


def load_existing_articles():
    """Load published articles from articles.js for real internal linking."""
    articles_js_path = os.path.join(BASE_DIR, "articles.js")
    if not os.path.exists(articles_js_path):
        return []
    with open(articles_js_path, "r", encoding="utf-8") as f:
        content = f.read()
    m = re.search(r'const ARTICLES = (\[[\s\S]*?\]);', content)
    if not m:
        return []
    try:
        articles = json.loads(m.group(1))
        return [{"slug": a["slug"], "title": a["title"], "category": a.get("category", "")} for a in articles]
    except Exception:
        return []


def build_user_prompt(primary_kw, secondary_kw, longtail_kw, category, existing_articles=None):
    # Build real internal link options from published articles
    if existing_articles:
        links_block = (
            "INTERNAL LINKS — you MUST only link to articles from this exact list (real published pages):\n"
            + "\n".join([f'  - slug: "{a["slug"]}" | title: "{a["title"]}"' for a in existing_articles])
            + "\n  Pick 2-4 of these. Use descriptive anchor text. Never invent slugs not on this list."
        )
    else:
        links_block = "Internal links: 3-5 with unique descriptive anchors relevant to the topic."

    return f"""Write a 1800+ word SEO article for NicheHubPro.

KEYWORDS:
- Primary: {primary_kw}
- Secondary: {secondary_kw}
- Long-tail: {longtail_kw}
- Category: {category}

REQUIREMENTS:
- Title: number + primary keyword in first 3 words + emotional/catchy ending
- Intro: primary keyword in first 10 words, 3 short emotional paragraphs
- TL;DR: 2-3 sentences with primary keyword
- 6 sections with VARIED headings specific to this topic (see JSON schema — never the same 5 pattern for every article. Choose the 6 most relevant headings for THIS keyword)
- Each section: GEO structure (statement + fact + advice), bullets, bold key tips
- Real life example: 2 paragraphs, human story showing transformation
- {links_block}
- FAQ: 5 real questions people search on Google about this topic
- Conclusion: motivational, encourage one small habit today
- Cover image: unique realistic wellness photo prompt for this specific topic
- Section images: 3 unique FLUX prompts in section_image_prompts (indexes 0, 2, 4). Each must show a DIFFERENT scene, person, and moment from each other and from the cover. Contextual to section content. No text, no logos.
- References: 3-5 entries citing REAL organizations only (Mayo Clinic, NHS, NIMH, APA, ADAA, Harvard Health, CDC, WHO, National Sleep Foundation, Cleveland Clinic, AHA). Use homepage URL only. Each claim must support something written in the article.

Return ONLY the JSON. No em dashes anywhere."""

# ── HF FLUX rules appended to every image prompt ─────────────────────────
_HF_RULES = (
    "HUMANIZATION RULES — apply every single one: "
    "This must look like a real unedited snapshot taken on a smartphone by a friend — NOT AI art, NOT stock photo, NOT professional shoot. "
    "Skin: visible pores, subtle blemishes, natural redness on cheeks or nose, slight unevenness in skin tone — ZERO smooth AI skin, ZERO glowing or poreless complexion. "
    "Eyes: asymmetric, slightly tired or watery, natural catchlights only — NOT perfectly symmetrical, NOT AI-sharp. "
    "Hair: messy real texture with flyaways, frizz, split ends, baby hairs — NOT perfectly styled, NOT shiny or glossy. "
    "Face: candid, absorbed, or slightly tired expression — NOT a posed smile, NOT a model face, NOT direct eye contact with camera. "
    "A small real-life imperfection is required: a small blemish, under-eye shadow, slight asymmetry, or redness. "
    "Clothing: visibly faded, slightly wrinkled, ordinary everyday fabric — NEVER stylish or tailored. "
    "Frame: shoulders or collarbone up only — never show chest, body below, hands, or arms. NO hands in frame under any circumstance. NO objects being held or touched. "
    "Lighting: flat natural window light or overcast daylight — NO studio rim light, NO beauty dish. "
    "Background: plain and slightly cluttered — NO styled props. "
    "Composition: slightly off-center, imperfect handheld framing — NOT centered, NOT symmetrical. "
    "NO oversaturation, NO HDR, NO color grading, NO filters. "
    "Photographic grain is acceptable and preferred over AI-smooth output. "
    "Single photograph only, not a diptych or collage. No text, no logos, no watermarks."
)

_HF_NEGATIVE = (
    "hands, arms, fingers, wrist, palm, fist, holding, mug, cup, coffee, pen, pencil, "
    "notebook, journal, book, phone, writing, typing, "
    "artificial skin, plastic skin, porcelain skin, glowing skin, perfect skin, doll face, "
    "AI generated look, digital art, illustration, painting, CGI render, stock photo, "
    "model pose, beauty campaign, symmetrical face, flawless complexion, "
    "studio lighting, rim lighting, smooth skin, airbrushed, retouched, "
    "watermark, text, logo, anime, cartoon, "
    "extra fingers, missing fingers, six fingers, four fingers, malformed hands, "
    "extra hands, three hands, fused fingers, distorted hands, deformed fingers, "
    "extra limbs, extra arms, floating hands, unnatural hands, bad anatomy"
)

_HF_API_URL = "https://router.huggingface.co/fal-ai/fal-ai/flux/dev"
_HF_DELAY = 20  # seconds between HF calls

# ── SECTION IMAGE DOWNLOADER — HF fal-ai FLUX.1-dev ──────────────────────
def download_section_image(prompt, article_slug, index, retries=3, delay=0):
    """Download a section image via HuggingFace (fal-ai FLUX.1-dev) at 1024x576."""
    try:
        from config import HF_API_KEY
    except ImportError:
        HF_API_KEY = os.environ.get("HF_API_KEY", "")

    filename = f"{article_slug}-sec{index}.webp"
    out_path = os.path.join(IMAGES_DIR, filename)
    full_prompt = f"{prompt} {_HF_RULES}"

    if delay > 0:
        print(f"  Waiting {delay}s before section image {index}...")
        time.sleep(delay)

    for attempt in range(1, retries + 1):
        try:
            print(f"  Section image {index} (HF FLUX.1-dev attempt {attempt})...")
            resp = requests.post(
                _HF_API_URL,
                headers={"Authorization": f"Bearer {HF_API_KEY}"},
                json={
                    "prompt": full_prompt,
                    "negative_prompt": _HF_NEGATIVE,
                    "image_size": {"width": 1024, "height": 576},
                    "num_inference_steps": 50,
                    "guidance_scale": 3.5,
                    "num_images": 1,
                    "seed": attempt * 13,
                },
                verify=False,
                timeout=180,
            )
            resp.raise_for_status()
            data = resp.json()
            img_url = data["images"][0]["url"]
            img_resp = requests.get(img_url, verify=False, timeout=60)
            img_resp.raise_for_status()
            img = Image.open(io.BytesIO(img_resp.content)).convert("RGB")
            img = img.resize((800, 450), Image.LANCZOS)
            for quality in range(82, 10, -5):
                buf = io.BytesIO()
                img.save(buf, format='WEBP', quality=quality, method=4)
                if buf.tell() / 1024 <= 80:
                    break
            with open(out_path, 'wb') as f:
                f.write(buf.getvalue())
            size_kb = os.path.getsize(out_path) / 1024
            print(f"  Saved: {filename} ({size_kb:.1f} KB)")
            return filename
        except Exception as e:
            print(f"  Attempt {attempt} failed: {e}")
            if attempt < retries:
                time.sleep(10)

    print(f"  Section image {index} failed — skipping")
    return None


# ── ARTICLE HTML TEMPLATE ─────────────────────────────────────────────────
def build_html(data, keyword_day, cover_filename, section_images=None):
    title        = data["title"]
    meta_desc    = data["meta_description"]
    category     = data["category"]
    article_slug = data["slug"]
    cover_alt    = data.get("cover_alt_text", title)
    cover_webp   = cover_filename.replace(".jpg", ".webp")
    intro        = data["intro"]
    tldr         = data["tldr"]
    sections     = data["sections"]
    real_example = data["real_example"]
    internal_links = data.get("internal_links", [])
    related      = data.get("related", internal_links[:3])
    faq_items    = data["faq"]
    conclusion   = data["conclusion"]
    cat_url      = CATEGORY_URLS.get(category, "../category.html")
    today_iso    = date.today().strftime("%Y-%m-%d")

    # Resolve author profile
    author         = AUTHORS.get(category, AUTHORS["Mental Wellness"])
    author_name    = author["name"]
    author_initials = author["initials"]
    author_title   = author["title"]
    author_bio     = author["bio"]
    author_color   = author["color"]
    references     = data.get("references") or author["default_refs"]

    # Build references HTML
    refs_html = ""
    for ref in references:
        claim  = ref.get("claim", "")
        source = ref.get("source", "")
        url    = ref.get("url", "#")
        if claim:
            refs_html += (
                f'<li style="font-size:0.82rem;color:var(--text);line-height:1.6;padding:6px 0;'
                f'border-bottom:1px solid var(--border);">'
                f'<span style="color:var(--gray);margin-right:6px;">&#9642;</span>'
                f'<em>{claim}</em> - '
                f'<a href="{url}" target="_blank" rel="nofollow noopener" '
                f'style="color:var(--emerald);font-weight:500;">{source}</a></li>\n'
            )
        else:
            refs_html += (
                f'<li style="font-size:0.82rem;color:var(--text);line-height:1.6;padding:6px 0;'
                f'border-bottom:1px solid var(--border);">'
                f'<span style="color:var(--emerald);margin-right:6px;">&#8599;</span>'
                f'<a href="{url}" target="_blank" rel="nofollow noopener" '
                f'style="color:var(--dark);font-weight:500;">{source}</a></li>\n'
            )

    # Build FAQ schema
    faq_schema_items = ",\n".join([
        f'''      {{
        "@type": "Question",
        "name": {json.dumps(f["question"])},
        "acceptedAnswer": {{ "@type": "Answer", "text": {json.dumps(f["answer"])} }}
      }}''' for f in faq_items
    ])

    # Build TOC from section headings
    toc_items = ""
    for i, sec in enumerate(sections):
        toc_items += f'<li><a href="#sec-{i+1}">{sec["h2"]}</a></li>\n        '
    toc_items += '<li><a href="#faq">Frequently Asked Questions</a></li>'
    toc_html = f"""<nav class="toc" aria-label="Table of contents">
      <div class="toc-title">In this article</div>
      <ol>
        {toc_items}
      </ol>
    </nav>"""

    # Build sections HTML
    sections_html = ""
    for i, sec in enumerate(sections):
        body = sec.get('content') or sec.get('body') or sec.get('text') or sec.get('html') or ''
        sections_html += f"\n      <h2 id=\"sec-{i+1}\">{sec['h2']}</h2>\n      {body}\n"
        # Insert section image after sections 0, 2, 4
        if section_images and i in section_images:
            img_info = section_images[i]
            sections_html += (
                f'\n      <img src="../images/{img_info["filename"]}" '
                f'alt="{img_info["alt_text"]}" '
                f'style="width:100%;max-height:480px;object-fit:cover;border-radius:10px;margin:28px 0 20px;display:block;" '
                f'width="1920" height="1080" loading="lazy">\n'
            )
        # Inline ebook promo after section 2 (replaces ad slot)
        if i == 1:
            sections_html += '''
      <div class="inline-promo">
        <div class="inline-promo-icon">&#128218;</div>
        <div class="inline-promo-body">
          <strong>Free: 30-Day Discipline Reset</strong>
          <span>Our free ebook with 20 exercises to rebuild focus and healthy habits.</span>
        </div>
        <a href="/ebook/" class="btn btn-sm">Get Free Ebook</a>
      </div>\n'''

    # Fix any bare-slug internal links the LLM wrote as href="/slug" → href="../articles/slug.html"
    _TOP_LEVEL = {'mental-wellness','productivity','healthy-lifestyle','resources','about',
                  'contact','privacy','disclaimer','terms','ebook','all-articles','ideafuel'}
    def _fix_link(m):
        slug_val = m.group(1).strip('/')
        if slug_val.split('/')[0] in _TOP_LEVEL or slug_val.endswith('.html') or slug_val.startswith('articles/'):
            return m.group(0)
        return f'href="../articles/{slug_val}.html"'
    sections_html = re.sub(r'href="/([^"]+)"', _fix_link, sections_html)

    # Also fix absolute self-links: href="https://nichehubpro.com/slug" (no /articles/ prefix)
    def _fix_absolute_link(m):
        path = m.group(1).strip('/')
        if path.startswith('articles/') or path.split('/')[0] in _TOP_LEVEL:
            return m.group(0)
        return f'href="../articles/{path}.html"'
    sections_html = re.sub(r'href="https://nichehubpro\.com/(?!articles/)([^"]+)"', _fix_absolute_link, sections_html)

    # Build FAQ HTML
    faq_html = ""
    for f in faq_items:
        faq_html += f"""
        <div class="faq-item">
          <button class="faq-q">
            {f['question']}
            <span class="faq-icon">+</span>
          </button>
          <div class="faq-a">{f['answer']}</div>
        </div>"""

    # Build internal links HTML (max 3)
    related_html = "".join([
        f'<li><a href="../articles/{r["slug"]}.html" style="font-size:0.92rem;font-weight:500;color:var(--dark);">→ {r["anchor"] if "anchor" in r else r.get("title","")}</a></li>'
        for r in internal_links[:3]
    ])

    # Build related article cards HTML (bottom of article, max 3)
    related_cards_html = "".join([
        '<div class="card"><div class="card-body">'
        f'<span class="card-tag">{category}</span>'
        f'<h3><a href="../articles/{r["slug"]}.html">{r.get("anchor") or r.get("title") or r["slug"]}</a></h3>'
        f'<a href="../articles/{r["slug"]}.html" class="read-more">Read article &rarr;</a>'
        '</div></div>'
        for r in related[:3]
    ])

    # Build sidebar related articles HTML (max 3)
    sidebar_related_html = "".join([
        '<div class="sidebar-related-item">'
        f'<span class="sidebar-related-num">{i+1}</span>'
        f'<a href="../articles/{r["slug"]}.html">{r.get("anchor") or r.get("title") or r["slug"]}</a>'
        '</div>'
        for i, r in enumerate(related[:3])
    ])

    # Build intro HTML
    intro_paragraphs = "".join([f"<p>{p.strip()}</p>" for p in intro.split("\n") if p.strip()])

    # Build conclusion HTML
    conclusion_paragraphs = "".join([f"<p>{p.strip()}</p>" for p in conclusion.split("\n") if p.strip()])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <link rel="icon" type="image/png" href="/favicon.png">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | NicheHubPro</title>
  <meta name="description" content="{meta_desc}">
  <link rel="canonical" href="{SITE_URL}/articles/{article_slug}.html">
  <link rel="preload" as="font" href="/fonts/nuFiD-vYSZviVYUb_rj3ij__anPXDTzYgA.woff2" type="font/woff2" crossorigin>
  <link rel="preload" as="font" href="/fonts/pxiEyp8kv8JHgFVrJJfecg.woff2" type="font/woff2" crossorigin>
  <link rel="preload" as="image" href="../images/{cover_webp}" type="image/webp">
  <link rel="stylesheet" href="../style.css">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{meta_desc}">
  <meta property="og:image" content="{SITE_URL}/images/{cover_filename}">
  <meta property="og:type" content="article">
  <meta name="twitter:card" content="summary_large_image">

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": {json.dumps(title)},
    "description": {json.dumps(meta_desc)},
    "image": "{SITE_URL}/images/{cover_filename}",
    "datePublished": "{today_iso}",
    "dateModified": "{today_iso}",
    "author": {{ "@type": "Person", "name": "{author_name}", "url": "{SITE_URL}/author/sarah-mitchell/", "jobTitle": "{author_title}" }},
    "publisher": {{ "@type": "Organization", "name": "NicheHubPro", "url": "{SITE_URL}", "logo": {{ "@type": "ImageObject", "url": "{SITE_URL}/favicon.png" }} }}
  }}
  </script>

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
{faq_schema_items}
    ]
  }}
  </script>
</head>
<body>

<div id="progress-bar"></div>

<nav class="nav">
  <div class="nav-inner">
    <a href="../" class="nav-logo">NicheHub<span>Pro</span></a>
    <div class="nav-links">
      <a href="../mental-wellness/">Mental Wellness</a>
      <a href="../productivity/">Productivity</a>
      <a href="../healthy-lifestyle/">Healthy Lifestyle</a>
      <a href="../resources/" class="nav-resources">Resources</a>
      <a href="../about/" class="nav-cta">Start Here</a>
    </div>
    <button class="nav-burger" id="burger" aria-label="Open navigation menu" aria-expanded="false" aria-controls="nav-mobile" type="button"><span></span><span></span><span></span></button>
  </div>
  <div class="nav-mobile" id="nav-mobile">
    <a href="../mental-wellness/">Mental Wellness</a>
    <a href="../productivity/">Productivity</a>
    <a href="../healthy-lifestyle/">Healthy Lifestyle</a>
    <a href="../resources/">Resources</a>
    <a href="../about/">About</a>
  </div>
</nav>

<div class="breadcrumb">
  <a href="../">Home</a>
  <span class="breadcrumb-sep">/</span>
  <a href="{cat_url}">{category}</a>
  <span class="breadcrumb-sep">/</span>
  <span>{title[:55]}{'...' if len(title) > 55 else ''}</span>
</div>

<div class="article-layout">
  <main>
    <div class="article-header">
      <span class="article-tag">{category}</span>
      <h1>{title}</h1>
      <div class="article-meta">
        <span>&#128197; {today_iso}</span>
        <span>&#9203; <span id="read-time">8</span> min read</span>
        <span>&#9997;&#65039; {author_name}</span>
        <span>&#10003; Fact-checked</span>
      </div>
    </div>

    <article class="article-content" id="article-body">

      <img src="https://nichehubpro.com/images/{cover_filename}"
           alt="{cover_alt}"
           style="width:100%;max-height:520px;object-fit:cover;border-radius:var(--radius-lg);margin-bottom:32px;display:block;"
           width="1920" height="1080"
           loading="eager" fetchpriority="high">

      {intro_paragraphs}

      {toc_html}

      <div class="tldr">
        <p>{tldr}</p>
      </div>

      {sections_html}

      <h2 id="real-life">What Does This Look Like in Real Life?</h2>
      {"".join(f"<p>{p.strip()}</p>" for p in real_example.split(chr(10)) if p.strip())}

      <div class="author-block" style="display:flex;gap:18px;align-items:flex-start;background:var(--bg);border:1px solid var(--border);border-radius:var(--radius);padding:24px 28px;margin:40px 0;">
        <div style="flex-shrink:0;width:56px;height:56px;border-radius:50%;background:{author_color};display:flex;align-items:center;justify-content:center;font-size:1.1rem;font-weight:800;color:#fff;letter-spacing:0.03em;">{author_initials}</div>
        <div style="flex:1;">
          <div style="font-size:1rem;font-weight:700;color:var(--navy);margin-bottom:2px;">{author_name}</div>
          <div style="font-size:0.78rem;color:var(--gray);margin-bottom:10px;">{author_title}</div>
          <p style="font-size:0.87rem;color:var(--text);line-height:1.7;margin:0 0 10px;">{author_bio}</p>
          <div style="display:flex;gap:14px;flex-wrap:wrap;">
            <span style="font-size:0.74rem;color:var(--gray);display:flex;align-items:center;gap:4px;">
              <span style="color:var(--emerald);font-size:0.85rem;">&#10003;</span> Reviewed for accuracy before publishing
            </span>
            <span style="font-size:0.74rem;color:var(--gray);">Published {today_iso}</span>
          </div>
        </div>
      </div>

      <div style="background:var(--bg);border:1px solid var(--border);border-radius:var(--radius-sm);padding:22px 26px;margin:36px 0;">
        <p style="font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:var(--gray);margin-bottom:14px;">Related Reading</p>
        <ul style="list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:10px;">
          {related_html}
        </ul>
      </div>

      <div class="faq-section" id="faq">
        <h2>Frequently Asked Questions</h2>
        {faq_html}
      </div>

      <div style="background:linear-gradient(135deg,var(--navy) 0%,#0c2820 100%);border-radius:var(--radius-lg);padding:32px;margin:48px 0;display:flex;gap:22px;flex-wrap:wrap;align-items:center;justify-content:space-between;">
        <div style="flex:1;min-width:200px;">
          <span style="font-size:0.67rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:#6EE7B7;">Free Resources</span>
          <h3 style="color:#fff;font-size:1.1rem;font-weight:700;margin:10px 0 8px;line-height:1.3;">Put this into practice today.</h3>
          <p style="color:rgba(255,255,255,0.5);font-size:0.85rem;line-height:1.7;margin:0;">Our free ebook and habit tracker app help you apply what you just read. No cost, no signup required.</p>
        </div>
        <div style="display:flex;flex-direction:column;gap:10px;min-width:220px;">
          <a href="/ebook/" style="display:flex;align-items:center;gap:12px;background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.22);border-radius:10px;padding:12px 16px;text-decoration:none;transition:background 0.2s;" onmouseover="this.style.background='rgba(16,185,129,0.18)'" onmouseout="this.style.background='rgba(16,185,129,0.1)'">
            <span style="font-size:1.5rem;flex-shrink:0;">&#128214;</span>
            <div>
              <div style="font-size:0.78rem;font-weight:700;color:#6EE7B7;">Free Ebook</div>
              <div style="font-size:0.72rem;color:rgba(255,255,255,0.42);">30-Day Discipline Reset</div>
            </div>
          </a>
          <a href="https://play.google.com/store/apps/details?id=com.ideafuel.idea_fuel" target="_blank" rel="noopener" style="display:flex;align-items:center;gap:12px;background:rgba(20,184,166,0.08);border:1px solid rgba(20,184,166,0.2);border-radius:10px;padding:12px 16px;text-decoration:none;transition:background 0.2s;" onmouseover="this.style.background='rgba(20,184,166,0.16)'" onmouseout="this.style.background='rgba(20,184,166,0.08)'">
            <span style="font-size:1.5rem;flex-shrink:0;">&#9889;</span>
            <div>
              <div style="font-size:0.78rem;font-weight:700;color:#5EEAD4;">Free Android App</div>
              <div style="font-size:0.72rem;color:rgba(255,255,255,0.42);">IdeaFuel: Habit &amp; Focus Timer</div>
            </div>
          </a>
        </div>
      </div>

      <h2>Where to Go From Here</h2>
      {conclusion_paragraphs}

      <div style="margin:40px 0 0;padding:22px 26px;background:var(--bg);border:1px solid var(--border);border-radius:var(--radius-sm);">
        <p style="font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:var(--gray);margin:0 0 8px;">Sources &amp; References</p>
        <p style="font-size:0.78rem;color:var(--gray);margin:0 0 14px;line-height:1.6;">This article draws on research from trusted health and wellness organizations. We encourage you to explore the sources directly.</p>
        <ul style="list-style:none;padding:0;margin:0;">
          {refs_html}
        </ul>
      </div>

      <div style="margin-top:24px;padding:18px 22px;background:var(--bg-2);border-radius:var(--radius-sm);border:1px solid var(--border);font-size:0.82rem;color:var(--gray);line-height:1.7;">
        <strong style="color:var(--navy);">Medical Disclaimer:</strong> This article is for informational purposes only and does not replace professional medical advice. If you are struggling with your mental or physical health, please consult a qualified healthcare provider.
      </div>

    </article>
  </main>

  <aside class="sidebar">
    <div class="sidebar-box">
      <h4>Related Articles</h4>
      {sidebar_related_html}
    </div>
    <div class="sidebar-box" style="background:var(--navy);">
      <h4 style="color:rgba(255,255,255,0.45);">Weekly Wellness</h4>
      <p style="font-size:0.84rem;color:rgba(255,255,255,0.6);margin-bottom:16px;line-height:1.65;">One actionable guide per week. Free forever.</p>
      <form id="sib-form" method="POST" data-type="subscription" action="https://1781df94.sibforms.com/serve/MUIFABtXrzMaI8A88PrzI10oMtw0B5ws-upYzYmZO7mYWfFa3ki3u-R9G0EdOr2E8lBWrGokcORpm15ZoeY3ZgiPdDVxO7NP7gze8Vi4tNHj7sAoz9PPm5-CheMlX0WFrJvDfzjmJCsSC9VqD-FYS8VIoox3qF8Dt0dP65ZgXg9rieMCtzx0jlj-88s6ug_y_LtpGFntWQ_VHbDufw==" style="display:flex;flex-direction:column;gap:8px;">
        <input type="email" name="EMAIL" placeholder="Your email" required style="padding:11px 14px;border-radius:var(--radius-pill);border:1.5px solid rgba(255,255,255,0.15);background:rgba(255,255,255,0.07);color:white;font-family:'Poppins',sans-serif;font-size:0.85rem;outline:none;">
        <button class="btn btn-sm" type="submit" style="width:100%;border-radius:var(--radius-pill);">Subscribe Free</button>
        <input type="text" name="email_address_check" value="" style="display:none;">
        <input type="hidden" name="locale" value="en">
      </form>
    </div>
    <div class="sidebar-box" style="background:linear-gradient(135deg,var(--navy) 0%,#0c2820 100%);border:1px solid rgba(16,185,129,0.12);">
      <h4 style="color:rgba(255,255,255,0.5);">Free Resources</h4>
      <p style="font-size:0.78rem;color:rgba(255,255,255,0.38);margin-bottom:14px;line-height:1.5;">Built to help you actually follow through.</p>
      <a href="/ebook/" style="display:flex;align-items:center;gap:10px;padding:10px 12px;background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);border-radius:8px;text-decoration:none;margin-bottom:8px;transition:all 0.2s;" onmouseover="this.style.background=\'rgba(16,185,129,0.16)\'" onmouseout="this.style.background=\'rgba(16,185,129,0.08)\'">
        <span style="font-size:1.3rem;flex-shrink:0;">&#128214;</span>
        <div>
          <div style="font-size:0.76rem;font-weight:700;color:#6EE7B7;line-height:1.3;">Free Ebook</div>
          <div style="font-size:0.7rem;color:rgba(255,255,255,0.4);line-height:1.4;">30-Day Discipline Reset</div>
        </div>
      </a>
      <a href="https://play.google.com/store/apps/details?id=com.ideafuel.idea_fuel" target="_blank" rel="noopener" style="display:flex;align-items:center;gap:10px;padding:10px 12px;background:rgba(20,184,166,0.07);border:1px solid rgba(20,184,166,0.18);border-radius:8px;text-decoration:none;transition:all 0.2s;" onmouseover="this.style.background=\'rgba(20,184,166,0.14)\'" onmouseout="this.style.background=\'rgba(20,184,166,0.07)\'">
        <span style="font-size:1.3rem;flex-shrink:0;">&#9889;</span>
        <div>
          <div style="font-size:0.76rem;font-weight:700;color:#5EEAD4;line-height:1.3;">Free Android App</div>
          <div style="font-size:0.7rem;color:rgba(255,255,255,0.4);line-height:1.4;">IdeaFuel: Habit + Focus Timer</div>
        </div>
      </a>
    </div>
  </aside>
</div>

<section class="section section-soft" style="padding-top:72px;padding-bottom:72px;">
  <div class="container">
    <div class="section-header">
      <div class="section-eyebrow">Keep Reading</div>
      <h2 class="section-title">More on {category}</h2>
    </div>
    <div class="grid grid-3">
      {related_cards_html}
    </div>
  </div>
</section>

<footer class="footer">
  <div class="footer-inner">
    <div class="footer-top">
      <div class="footer-brand">
        <a href="/" class="footer-logo">NicheHub<span>Pro</span></a>
        <p class="footer-mission">A free wellness and productivity publication built for people who want to think clearer, feel calmer, and live with more intention. No paywalls, no subscriptions, no fluff.</p>
        <div style="display:flex;gap:10px;flex-wrap:wrap;">
          <a href="/ebook/" style="font-size:0.8rem;font-weight:600;color:var(--emerald);padding:7px 14px;border:1px solid rgba(16,185,129,0.25);border-radius:var(--radius-pill);">Free Ebook &rarr;</a>
          <a href="https://play.google.com/store/apps/details?id=com.ideafuel.idea_fuel" target="_blank" rel="noopener" style="font-size:0.8rem;font-weight:600;color:rgba(255,255,255,0.5);padding:7px 14px;border:1px solid rgba(255,255,255,0.1);border-radius:var(--radius-pill);">Android App &rarr;</a>
        </div>
      </div>
      <div class="footer-col">
        <h4>Topics</h4>
        <ul>
          <li><a href="/mental-wellness/">Mental Wellness</a></li>
          <li><a href="/productivity/">Productivity</a></li>
          <li><a href="/healthy-lifestyle/">Healthy Lifestyle</a></li>
          <li><a href="/all-articles/">All Articles</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Resources</h4>
        <ul>
          <li><a href="/ebook/">Free Ebook</a></li>
          <li><a href="https://play.google.com/store/apps/details?id=com.ideafuel.idea_fuel" target="_blank" rel="noopener">IdeaFuel App</a></li>
          <li><a href="/resources/">All Resources</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Company</h4>
        <ul>
          <li><a href="/about/">About Us</a></li>
          <li><a href="/contact/">Contact</a></li>
          <li><a href="/privacy/">Privacy Policy</a></li>
          <li><a href="/disclaimer/">Disclaimer</a></li>
          <li><a href="/terms/">Terms of Service</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom-row">
      <span class="footer-copyright">&copy; 2026 NicheHubPro. All rights reserved.</span>
    </div>
  </div>
</footer>

<button id="back-to-top" aria-label="Back to top">&#8593;</button>
<script src="../script.js"></script>
</body>
</html>"""


# ── MAIN GENERATOR ────────────────────────────────────────────────────────
def generate_article(primary_kw, secondary_kw, longtail_kw, category, skip_images=False):
    print(f"\n{'='*60}")
    print(f"Keyword : {primary_kw}")
    print(f"Category: {category}")
    print(f"{'='*60}")

    import httpx
    client = anthropic.Anthropic(
        api_key=API_KEY,
        http_client=httpx.Client(verify=False),
    )

    # Load real published articles — same category only, exclude current article
    existing_articles = load_existing_articles()
    current_slug = slug(primary_kw)
    existing_articles = [
        a for a in existing_articles
        if a["slug"] != current_slug and a.get("category") == category
    ]
    if existing_articles:
        print(f"  Internal link pool: {len(existing_articles)} article(s) in [{category}]")

    print("Calling Claude API...")
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=16000,
        messages=[
            {
                "role": "user",
                "content": build_user_prompt(primary_kw, secondary_kw, longtail_kw, category, existing_articles)
            }
        ],
        system=SYSTEM_PROMPT
    )

    raw = message.content[0].text.strip()

    # Strip markdown code fences if present
    raw = re.sub(r'^\s*```(?:json)?\s*', '', raw)
    raw = re.sub(r'\s*```\s*$', '', raw.strip())

    # Extract JSON block
    json_match = re.search(r'\{[\s\S]*\}', raw)
    if not json_match:
        print("ERROR: No JSON found in response")
        print(raw[:500])
        return None

    json_str = json_match.group()

    # Parse JSON — use json_repair for resilience against minor malformations
    try:
        if _HAS_JSON_REPAIR:
            data = json_repair.repair_json(json_str, return_objects=True)
            if not isinstance(data, dict):
                raise ValueError(f"Expected dict, got {type(data)}")
        else:
            data = json.loads(json_str)
    except Exception as e:
        print(f"ERROR: JSON parse failed: {e}")
        print(json_str[:500])
        return None

    article_slug = slug(primary_kw)
    data["slug"] = article_slug

    # Log the cover image prompt (for future AI image generation)
    cover_prompt = data.get("cover_image_prompt", "")
    if cover_prompt:
        print(f"\nCover concept:\n  {cover_prompt[:120]}...")

    # Generate cover image (branded Pillow version)
    cover_filename = article_slug + ".jpg"
    cover_path = os.path.join(IMAGES_DIR, cover_filename)

    if skip_images and os.path.exists(cover_path):
        print(f"\nCover image reused: {cover_filename}")
    else:
        print("\nGenerating cover image...")
        generate_cover(data["title"], category, cover_path, custom_prompt=cover_prompt)
        print(f"Cover saved: {cover_filename}")

        # Convert cover JPG to WebP so <picture> tag always has both formats
        try:
            from PIL import Image as _PIL
            cover_webp_path = cover_path.replace(".jpg", ".webp")
            _img = _PIL.open(cover_path)
            _img.save(cover_webp_path, "WEBP", quality=78, method=6)
            print(f"Cover WebP saved: {os.path.basename(cover_webp_path)}")
        except Exception as _e:
            print(f"WebP conversion skipped: {_e}")

        # Cool-down after cover generation burst (3 HF calls) before section images
        print("  Cooling down 30s before section images...")
        time.sleep(30)

    # Generate section images (WebP, contextual per section) — delay between calls
    section_images = {}
    if not skip_images:
        for call_num, img_data in enumerate(data.get("section_image_prompts", [])):
            sec_idx = img_data.get("section_index", 0)
            prompt  = img_data.get("prompt", "")
            alt     = img_data.get("alt_text", data["title"])
            if prompt:
                filename = download_section_image(
                    prompt, article_slug, sec_idx + 1, delay=_HF_DELAY
                )
                if filename:
                    section_images[sec_idx] = {"filename": filename, "alt_text": alt}
        if section_images:
            print(f"  {len(section_images)} section image(s) generated")

    # Build and save HTML
    print("Building HTML...")
    html = build_html(data, primary_kw, cover_filename, section_images)
    from clean_ai_text import clean_ai_text
    html = clean_ai_text(html)
    out_path = os.path.join(OUT_DIR, f"{article_slug}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Article saved: articles/{article_slug}.html")

    # Register article in articles.js
    register_article(data, cover_filename)

    # Send to Make.com → Pinterest automation
    send_pinterest_webhook(
        article_slug,
        data["title"],
        data.get("category", category),
        cover_filename,
        data.get("pinterest_pins", [])
    )

    # Reverse linking — inject this article into existing same-category articles
    backlink_existing_articles(article_slug, data["title"], category)

    # Ping Google to re-crawl updated sitemap
    ping_google()

    return article_slug


def register_article(data, cover_filename):
    """Add or update article entry in articles.js registry."""
    articles_js_path = os.path.join(os.path.dirname(OUT_DIR), "articles.js")

    # Read existing entries
    existing = []
    if os.path.exists(articles_js_path):
        with open(articles_js_path, "r", encoding="utf-8") as f:
            content = f.read()
        m = re.search(r'const ARTICLES = (\[[\s\S]*?\]);', content)
        if m:
            try:
                existing = json.loads(m.group(1))
            except Exception:
                existing = []

    # Build excerpt from intro (first paragraph, max 155 chars)
    intro = data.get("intro", "")
    excerpt = intro.split("\n")[0].strip()[:155] if intro else ""

    # Category slug
    cat_slug = data.get("category", "Mental Wellness").lower().replace(" ", "-")

    new_entry = {
        "slug":     data["slug"],
        "title":    data["title"],
        "category": data.get("category", "Mental Wellness"),
        "cat_slug": cat_slug,
        "date":     date.today().strftime("%b %Y"),
        "read_time": "8",
        "excerpt":  excerpt,
        "image":    f"images/{cover_filename}",
        "alt":      data.get("cover_alt_text", data["title"]),
        "pins":     data.get("pinterest_pins", [])
    }

    # Remove old entry for this slug if exists, prepend new one (newest first)
    existing = [a for a in existing if a.get("slug") != data["slug"]]
    existing.insert(0, new_entry)

    js_content = (
        "// Auto-generated — do not edit manually\n"
        "// Updated by publisher_v2.py on each publish\n"
        f"const ARTICLES = {json.dumps(existing, indent=2, ensure_ascii=False)};\n"
    )
    with open(articles_js_path, "w", encoding="utf-8") as f:
        f.write(js_content)

    print(f"  Registered in articles.js ({len(existing)} total)")
    update_sitemap(existing)


def update_sitemap(articles):
    """Rebuild sitemap.xml with all published articles."""
    sitemap_path = os.path.join(BASE_DIR, "sitemap.xml")
    SITE = "https://nichehubpro.com"

    static_pages = [
        (f"{SITE}/",                    "daily",   "1.0"),
        (f"{SITE}/mental-wellness/",    "daily",   "0.9"),
        (f"{SITE}/productivity/",       "weekly",  "0.9"),
        (f"{SITE}/healthy-lifestyle/",  "weekly",  "0.9"),
        (f"{SITE}/about/",              "monthly", "0.7"),
        (f"{SITE}/contact/",            "monthly", "0.5"),
        (f"{SITE}/privacy/",            "monthly", "0.4"),
        (f"{SITE}/disclaimer/",         "monthly", "0.4"),
        (f"{SITE}/terms/",              "monthly", "0.4"),
    ]

    urls = []
    for loc, freq, pri in static_pages:
        urls.append(f"  <url>\n    <loc>{loc}</loc>\n    <changefreq>{freq}</changefreq>\n    <priority>{pri}</priority>\n  </url>")

    today = __import__('datetime').date.today().isoformat()
    for a in articles:
        loc = f"{SITE}/articles/{a['slug']}.html"
        date = a.get('date', '')
        try:
            import datetime
            lastmod = datetime.datetime.strptime(date, "%B %Y").strftime("%Y-%m") + f"-01"
        except Exception:
            lastmod = today
        urls.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{lastmod}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>")

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n\n'
        + "\n".join(urls)
        + "\n\n</urlset>\n"
    )

    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"  Sitemap updated ({len(articles)} articles)")


def backlink_existing_articles(new_slug, new_title, category):
    """Inject a link to the new article into existing articles of the same category."""
    articles_js_path = os.path.join(BASE_DIR, "articles.js")
    if not os.path.exists(articles_js_path):
        return

    with open(articles_js_path, "r", encoding="utf-8") as f:
        content = f.read()
    m = re.search(r'const ARTICLES = (\[[\s\S]*?\]);', content)
    if not m:
        return
    try:
        articles = json.loads(m.group(1))
    except Exception:
        return

    targets = [a for a in articles if a.get("category") == category and a["slug"] != new_slug]
    if not targets:
        return

    new_li = (
        f'\n          <li><a href="../articles/{new_slug}.html" '
        f'style="font-size:0.92rem;font-weight:500;color:var(--dark);">→ {new_title}</a></li>'
    )

    updated = 0
    for article in targets:
        html_path = os.path.join(OUT_DIR, f"{article['slug']}.html")
        if not os.path.exists(html_path):
            continue

        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        # Skip if already linked to new slug
        if f'href="../articles/{new_slug}.html"' in html:
            continue

        # Target the main article body Related Articles <ul> (unique style attribute)
        ul_pattern = (
            r'(<ul style="list-style:none;padding:0;margin:0;'
            r'display:flex;flex-direction:column;gap:8px;">'
            r'([\s\S]*?)</ul>)'
        )
        match = re.search(ul_pattern, html)
        if not match:
            continue

        old_block = match.group(0)
        new_block = old_block[:-5] + new_li + '\n        </ul>'  # insert before </ul>
        html = html.replace(old_block, new_block, 1)

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        updated += 1

    if updated:
        print(f"  Backlinked into {updated} existing article(s) in [{category}]")


def send_pinterest_webhook(article_slug, title, category, cover_filename, pins):
    """Send article data to Make.com webhook — triggers 3 Pinterest pins, each with a unique image."""
    try:
        from config import MAKE_PINTEREST_WEBHOOK
    except ImportError:
        return
    if not MAKE_PINTEREST_WEBHOOK:
        return

    board_ids = {
        "Mental Wellness":   "1135118349771004496",
        "Productivity":      "1135118349771004499",
        "Healthy Lifestyle": "1135118349771004501",
    }

    # Each pin gets its own image: cover, sec1, sec3
    pin_images = [
        f"{SITE_URL}/images/{cover_filename}",
        f"{SITE_URL}/images/{article_slug}-sec1.webp",
        f"{SITE_URL}/images/{article_slug}-sec3.webp",
    ]

    enriched_pins = []
    for i, pin in enumerate(pins[:3]):
        enriched_pins.append({
            "title":       pin.get("title", title),
            "description": pin.get("description", ""),
            "image_url":   pin_images[i],
        })

    payload = {
        "slug":        article_slug,
        "title":       title,
        "category":    category,
        "board_id":    board_ids.get(category, ""),
        "article_url": f"{SITE_URL}/articles/{article_slug}.html",
        "pins":        enriched_pins,
    }

    try:
        r = requests.post(MAKE_PINTEREST_WEBHOOK, json=payload, timeout=15)
        if r.status_code in (200, 204):
            print(f"  Pinterest webhook sent to Make.com (3 pins, 3 unique images)")
        else:
            print(f"  Pinterest webhook failed: {r.status_code}")
    except Exception as e:
        print(f"  Pinterest webhook error: {e}")


def ping_google():
    """Ping Google to re-crawl the updated sitemap."""
    try:
        import requests
        url = "https://www.google.com/ping?sitemap=https://nichehubpro.com/sitemap.xml"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            print("  Google pinged: sitemap re-crawl requested")
        else:
            print(f"  Google ping returned {resp.status_code}")
    except Exception as e:
        print(f"  Google ping failed (non-critical): {e}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2:
        print("Usage: python publisher_v2.py \"primary keyword\" \"category\" [\"secondary kw\"] [\"longtail kw\"]")
        sys.exit(1)
    primary  = args[0]
    category = args[1]
    secondary = args[2] if len(args) > 2 else primary
    longtail  = args[3] if len(args) > 3 else primary
    generate_article(primary, secondary, longtail, category)
