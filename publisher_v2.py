"""
NicheHubPro — Article Publisher v2
Generates a full SEO article HTML file from a keyword using Claude API.
Follows the exact article template + generates cover image.

Usage:
  python publisher_v2.py "how to stop overthinking at night" "Mental Wellness"
"""

import sys, os, re, json, textwrap, io, time
sys.stdout.reconfigure(encoding='utf-8')
import anthropic
import requests
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

# ── SYSTEM PROMPT ────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert SEO content writer for NicheHubPro, a mental wellness blog.
Your audience: real people dealing with stress, anxiety, and overthinking.
Your job: write human, motivational, deeply useful articles — NOT robotic AI content.

ABSOLUTE WRITING RULES (never break these):
- NEVER use em dashes (—) anywhere in the output
- NEVER use the word "delve"
- NEVER write "In today's fast-paced world", "It is important to note", "In conclusion"
- NEVER repeat the same anchor text for internal links
- Keep ALL paragraphs SHORT (2-3 lines max, strictly)
- Simple, clear English — write like a knowledgeable friend
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
      "h2": "string — question-based heading (What is X? / What are the signs? / Why does it happen? / How to fix it? / How to manage X daily?)",
      "content": "string — full HTML. Use <p>, <ul><li>, <strong>. Every <p> max 3 lines. GEO structure per paragraph. At least one <ul> list. At least one <strong> key advice. Min 200 words per section."
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
  "cover_image_prompt": "string — UNIQUE humanized photo prompt for THIS article. RULES: (1) Subject MUST be a young woman 25-35, OR close-up of hands only, OR environment with no person — NEVER a man. (2) Use candid documentary photography language. (3) Include specific details: hair color/style, exact clothing item, specific object she holds or touches. (4) Include camera style: 'shot on 85mm f/1.8, shallow depth of field, slightly blurred background'. (5) Include 'real skin texture, natural imperfections, no plastic look'. STRUCTURE: 'Candid lifestyle photo: a young woman, [age], [specific location and time of day]. [Hair and clothing details]. [Exact action and emotional expression]. [One specific prop or environmental detail]. [Lighting details]. Shot on 85mm f/1.8, shallow depth of field. Real skin texture, natural imperfections. Photorealistic documentary photography. No text, no logos, no watermarks, no AI look, no man.' FORBIDDEN: man, male, arms crossed, fake smile, stock photo pose, studio lighting, perfect symmetry.",
  "cover_alt_text": "string — short SEO alt text. Format: '[woman/hands/scene] [action] in [setting]'. Max 10 words. Include primary keyword.",
  "section_image_prompts": [
    {
      "section_index": 0,
      "prompt": "string — UNIQUE humanized photo prompt for section 1 image. RULES: young woman OR hands-only OR environment — NEVER a man. Must be completely different scene from cover. Use candid documentary style with specific details: exact setting, exact clothing, specific object, camera style (50mm or 85mm, f/1.8-2.8, shallow DOF), real skin texture. Tied to section 1 topic. No text, no logos, no man.",
      "alt_text": "string — 8-10 words describing the scene, include primary keyword"
    },
    {
      "section_index": 2,
      "prompt": "string — UNIQUE humanized photo prompt for section 3 image. RULES: young woman OR hands-only close-up OR outdoor/indoor environment — NEVER a man. Completely different from cover and section 1. Specific candid moment with exact details. Solution or progress-focused scene. Camera style included. No text, no logos, no man.",
      "alt_text": "string — 8-10 words describing the scene, include primary keyword"
    },
    {
      "section_index": 4,
      "prompt": "string — UNIQUE humanized photo prompt for section 5 image. RULES: young woman OR hands-only OR calm environment — NEVER a man. Different from all above images. Calming, hopeful, empowering candid moment. Specific props, lighting, clothing. Camera style included. No text, no logos, no man.",
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
- 5 question-based H2 sections (What is / Signs / Why it happens / How to fix / Daily habits)
- Each section: GEO structure (statement + fact + advice), bullets, bold key tips
- Real life example: 2 paragraphs, human story showing transformation
- {links_block}
- FAQ: 5 real questions people search on Google about this topic
- Conclusion: motivational, encourage one small habit today
- Cover image: unique realistic wellness photo prompt for this specific topic
- Section images: 3 unique FLUX prompts in section_image_prompts (indexes 0, 2, 4). Each must show a DIFFERENT scene, person, and moment from each other and from the cover. Contextual to section content. No text, no logos.

Return ONLY the JSON. No em dashes anywhere."""

# ── HF FLUX rules appended to every image prompt ─────────────────────────
_HF_RULES = (
    "Editorial photograph. "
    "Head-and-shoulders crop only, chest not visible. "
    "Real human face and skin: visible pores, natural imperfections, genuine hair texture, authentic non-posed expression — not AI-smooth, not a model. "
    "Plain everyday clothing. "
    "Shot on Sony A7IV 85mm f/1.8, shallow depth of field, slightly blurred background. "
    "Sharp focus, 4K photorealistic. "
    "Single photograph only, not a diptych or collage. No text, no logos, no watermarks."
)

_HF_DELAY = 12  # seconds between HF calls to avoid rate limits

# ── SECTION IMAGE DOWNLOADER — HF FLUX.1-schnell ─────────────────────────
def download_section_image(prompt, article_slug, index, retries=2, delay=0):
    """Download a section image via HF FLUX.1-schnell."""
    from huggingface_hub import InferenceClient as HFClient
    try:
        from config import HF_API_KEY
    except ImportError:
        HF_API_KEY = os.environ.get("HF_API_KEY", "")

    filename = f"{article_slug}-sec{index}.webp"
    out_path = os.path.join(IMAGES_DIR, filename)
    full_prompt = f"{prompt} {_HF_RULES}"
    hf = HFClient(token=HF_API_KEY)

    if delay > 0:
        print(f"  Waiting {delay}s before section image {index}...")
        time.sleep(delay)

    for attempt in range(1, retries + 1):
        try:
            print(f"  Section image {index} (HF FLUX attempt {attempt})...")
            img = hf.text_to_image(full_prompt, model="black-forest-labs/FLUX.1-schnell", width=1280, height=720)
            img = img.resize((1920, 1080), Image.LANCZOS)
            for quality in range(92, 10, -5):
                buf = io.BytesIO()
                img.convert('RGB').save(buf, format='WEBP', quality=quality, method=4)
                if buf.tell() / 1024 <= 500:
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
    intro        = data["intro"]
    tldr         = data["tldr"]
    sections     = data["sections"]
    real_example = data["real_example"]
    internal_links = data.get("internal_links", [])
    related      = data.get("related", internal_links[:3])
    faq_items    = data["faq"]
    conclusion   = data["conclusion"]
    cat_url      = CATEGORY_URLS.get(category, "../category.html")

    # Build FAQ schema
    faq_schema_items = ",\n".join([
        f'''      {{
        "@type": "Question",
        "name": {json.dumps(f["question"])},
        "acceptedAnswer": {{ "@type": "Answer", "text": {json.dumps(f["answer"])} }}
      }}''' for f in faq_items
    ])

    # Build sections HTML
    sections_html = ""
    for i, sec in enumerate(sections):
        body = sec.get('content') or sec.get('body') or sec.get('text') or sec.get('html') or ''
        sections_html += f"\n      <h2>{sec['h2']}</h2>\n      {body}\n"
        # Insert section image after sections 0, 2, 4
        if section_images and i in section_images:
            img_info = section_images[i]
            sections_html += (
                f'\n      <img src="../images/{img_info["filename"]}" '
                f'alt="{img_info["alt_text"]}" '
                f'style="width:100%;border-radius:10px;margin:28px 0 20px;display:block;object-fit:cover;" '
                f'loading="lazy">\n'
            )
        # Insert ad slot after section 2
        if i == 1:
            sections_html += '\n      <div class="ad-slot ad-slot-banner">Advertisement</div>\n'

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

    # Build internal links HTML
    related_html = "".join([
        f'<li><a href="../articles/{r["slug"]}.html" style="font-size:0.92rem;font-weight:500;color:var(--dark);">→ {r["anchor"] if "anchor" in r else r.get("title","")}</a></li>'
        for r in internal_links
    ])

    # Build related article cards HTML (bottom of article)
    related_cards_html = "".join([
        '<div class="card"><div class="card-body">'
        f'<span class="card-tag">{category}</span>'
        f'<h3><a href="../articles/{r["slug"]}.html">{r.get("anchor") or r.get("title") or r["slug"]}</a></h3>'
        f'<a href="../articles/{r["slug"]}.html" class="read-more">Read article &rarr;</a>'
        '</div></div>'
        for r in related[:3]
    ])

    # Build sidebar related articles HTML
    sidebar_related_html = "".join([
        '<div class="sidebar-related-item">'
        f'<span class="sidebar-related-num">{i+1}</span>'
        f'<a href="../articles/{r["slug"]}.html">{r.get("anchor") or r.get("title") or r["slug"]}</a>'
        '</div>'
        for i, r in enumerate(related)
    ])

    # Build intro HTML
    intro_paragraphs = "".join([f"<p>{p.strip()}</p>" for p in intro.split("\n") if p.strip()])

    # Build conclusion HTML
    conclusion_paragraphs = "".join([f"<p>{p.strip()}</p>" for p in conclusion.split("\n") if p.strip()])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — NicheHubPro</title>
  <meta name="description" content="{meta_desc}">
  <link rel="canonical" href="{SITE_URL}/articles/{article_slug}.html">
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
    "datePublished": "2026-04-12",
    "dateModified": "2026-04-12",
    "author": {{ "@type": "Organization", "name": "NicheHubPro" }},
    "publisher": {{ "@type": "Organization", "name": "NicheHubPro", "url": "{SITE_URL}" }}
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
      <a href="../about/" class="nav-cta">Start Here</a>
    </div>
    <div class="nav-burger" id="burger"><span></span><span></span><span></span></div>
  </div>
  <div class="nav-mobile" id="nav-mobile">
    <a href="../mental-wellness/">Mental Wellness</a>
    <a href="../productivity/">Productivity</a>
    <a href="../healthy-lifestyle/">Healthy Lifestyle</a>
    <a href="../about/">About</a>
  </div>
</nav>

<div class="breadcrumb">
  <a href="../">Home</a>
  <span class="breadcrumb-sep">/</span>
  <a href="{cat_url}">{category}</a>
  <span class="breadcrumb-sep">/</span>
  <span>{title[:50]}{'...' if len(title) > 50 else ''}</span>
</div>

<div class="article-layout">
  <main>
    <div class="article-header">
      <span class="article-tag">{category}</span>
      <h1>{title}</h1>
      <div class="article-meta">
        <span>📅 April 2026</span>
        <span>⏱ <span id="read-time">8</span> min read</span>
        <span>✍️ NicheHubPro Editorial</span>
      </div>
    </div>

    <!-- COVER IMAGE -->
    <img src="../images/{cover_filename}"
         alt="{cover_alt}"
         style="width:100%;border-radius:12px;margin-bottom:28px;display:block;"
         loading="lazy">

    <article class="article-content" id="article-body">

      {intro_paragraphs}

      <div class="tldr">
        <p>{tldr}</p>
      </div>

      {sections_html}

      <h2>What Does This Look Like in Real Life?</h2>
      {"".join(f"<p>{p.strip()}</p>" for p in real_example.split(chr(10)) if p.strip())}

      <div class="ad-slot ad-slot-banner">Advertisement</div>

      <div style="background:var(--green-pale);border:1px solid var(--border);border-radius:var(--radius-sm);padding:20px 24px;margin:32px 0;">
        <p style="font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:var(--gray);margin-bottom:12px;">Related Articles</p>
        <ul style="list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:8px;">
          {related_html}
        </ul>
      </div>

      <div class="faq-section">
        <h2>Frequently Asked Questions</h2>
        {faq_html}
      </div>

      <h2>Where to Go From Here</h2>
      {conclusion_paragraphs}

      <div style="margin-top:40px;padding:16px 20px;background:var(--border2);border-radius:var(--radius-sm);font-size:0.78rem;color:var(--gray);line-height:1.6;">
        <strong>Disclaimer:</strong> This article is for informational purposes only and does not replace professional medical advice. If you are struggling, please consult a qualified healthcare provider.
      </div>

    </article>
  </main>

  <aside class="sidebar">
    <div class="ad-slot ad-slot-sidebar">Advertisement</div>
    <div class="sidebar-box">
      <h4>Related Articles</h4>
      {sidebar_related_html}
    </div>
    <div class="sidebar-box" style="background:var(--dark);">
      <h4 style="color:rgba(255,255,255,0.5);">Weekly Wellness</h4>
      <p style="font-size:0.85rem;color:rgba(255,255,255,0.65);margin-bottom:14px;line-height:1.6;">One actionable guide per week. Free forever.</p>
      <form id="sib-form" method="POST" data-type="subscription" action="https://1781df94.sibforms.com/serve/MUIFABtXrzMaI8A88PrzI10oMtw0B5ws-upYzYmZO7mYWfFa3ki3u-R9G0EdOr2E8lBWrGokcORpm15ZoeY3ZgiPdDVxO7NP7gze8Vi4tNHj7sAoz9PPm5-CheMlX0WFrJvDfzjmJCsSC9VqD-FYS8VIoox3qF8Dt0dP65ZgXg9rieMCtzx0jlj-88s6ug_y_LtpGFntWQ_VHbDufw==" style="display:flex;flex-direction:column;gap:8px;">
        <input type="email" name="EMAIL" placeholder="Your email" required style="padding:10px 14px;border-radius:6px;border:1px solid rgba(255,255,255,0.15);background:rgba(255,255,255,0.08);color:white;font-family:Poppins,sans-serif;font-size:0.85rem;outline:none;">
        <button class="btn btn-sm" type="submit" style="width:100%;">Subscribe Free</button>
        <input type="text" name="email_address_check" value="" style="display:none;">
        <input type="hidden" name="locale" value="en">
      </form>
    </div>
  </aside>
</div>

<section class="section section-white">
  <div class="container">
    <div class="section-header">
      <span class="section-label">Keep Reading</span>
      <h2 class="section-title">More on {category}</h2>
    </div>
    <div class="grid grid-3">
      {related_cards_html}
    </div>
  </div>
</section>

<footer class="footer">
  <div class="footer-inner">
    <div class="footer-links">
      <a href="/about/">About</a>
      <span class="sep">|</span>
      <a href="/contact/">Contact</a>
      <span class="sep">|</span>
      <a href="/privacy/">Privacy Policy</a>
      <span class="sep">|</span>
      <a href="/disclaimer/">Disclaimer</a>
      <span class="sep">|</span>
      <a href="/terms/">Terms of Service</a>
    </div>
    <div class="footer-bottom">
      <span>&copy; 2026 NicheHubPro. All rights reserved.</span>
    </div>
  </div>
</footer>

<button id="back-to-top" aria-label="Back to top">↑</button>
<script src="../script.js"></script>
</body>
</html>"""


# ── MAIN GENERATOR ────────────────────────────────────────────────────────
def generate_article(primary_kw, secondary_kw, longtail_kw, category):
    print(f"\n{'='*60}")
    print(f"Keyword : {primary_kw}")
    print(f"Category: {category}")
    print(f"{'='*60}")

    client = anthropic.Anthropic(api_key=API_KEY)

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
        model="claude-haiku-4-5-20251001",
        max_tokens=8192,
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
    print("\nGenerating cover image...")
    cover_filename = article_slug + ".jpg"
    cover_path = os.path.join(IMAGES_DIR, cover_filename)
    generate_cover(data["title"], category, cover_path, custom_prompt=cover_prompt)
    print(f"Cover saved: {cover_filename}")

    # Generate section images (WebP, contextual per section) — delay between calls
    section_images = {}
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
        "date":     "Apr 2026",
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

    for a in articles:
        loc = f"{SITE}/articles/{a['slug']}.html"
        urls.append(f"  <url>\n    <loc>{loc}</loc>\n    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>")

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
    """Send article data to Make.com webhook — triggers 3 Pinterest pins."""
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

    payload = {
        "slug":        article_slug,
        "title":       title,
        "category":    category,
        "board_id":    board_ids.get(category, ""),
        "image_url":   f"{SITE_URL}/images/{cover_filename}",
        "article_url": f"{SITE_URL}/articles/{article_slug}.html",
        "pins":        pins[:3]
    }

    try:
        r = requests.post(MAKE_PINTEREST_WEBHOOK, json=payload, timeout=15)
        if r.status_code in (200, 204):
            print(f"  Pinterest webhook sent to Make.com ({len(pins)} pins queued)")
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
