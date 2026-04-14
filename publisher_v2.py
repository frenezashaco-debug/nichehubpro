"""
NicheHubPro — Article Publisher v2
Generates a full SEO article HTML file from a keyword using Claude API.
Follows the exact article template + generates cover image.

Usage:
  python publisher_v2.py "how to stop overthinking at night" "Mental Wellness"
"""

import sys, os, re, json, textwrap
sys.stdout.reconfigure(encoding='utf-8')
import anthropic
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
  "cover_image_prompt": "string — UNIQUE AI image prompt for THIS article. Follow this exact structure: 'Create a realistic, high-quality blog cover image for an article about: [TOPIC]. Scene: [specific real-life environment reflecting the topic]. Subject: a single person expressing [specific emotion tied to topic] with natural body language. Details: authentic everyday setting, minimal clean background, soft textures. Lighting: soft natural [morning/evening] light, warm calming tones. Style: photorealistic, minimalist wellness aesthetic, depth of field, shot like a real camera. Mood: emotional but peaceful, relatable and human. Composition: subject slightly off-center, focus on emotion. STRICT: no text, no logos, no watermark, not stock photo. Output: 4K ultra realistic natural colors.' FORBIDDEN scenes: woman sitting by window, person meditating on bed, hands clasped, eyes closed in bedroom. Each image must feel like a unique candid moment.",
  "cover_alt_text": "string — short SEO alt text describing the image. Format: '[person/subject] [action] in [setting]'. Example: 'person overthinking at night in bedroom'. Max 10 words. Include the primary keyword naturally."
}"""


def build_user_prompt(primary_kw, secondary_kw, longtail_kw, category):
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
- Internal links: 3-5 with unique descriptive anchors — suggest topics like: how to stop overthinking, how to calm anxiety quickly, daily habits to reduce stress, morning routine for mental health, how to build discipline (match to article topic)
- FAQ: 5 real questions people search on Google about this topic
- Conclusion: motivational, encourage one small habit today
- Cover image: unique realistic wellness photo prompt for this specific topic

Return ONLY the JSON. No em dashes anywhere."""

# ── ARTICLE HTML TEMPLATE ─────────────────────────────────────────────────
def build_html(data, keyword_day, cover_filename):
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
      <form onsubmit="return false;" style="display:flex;flex-direction:column;gap:8px;">
        <input type="email" placeholder="Your email" style="padding:10px 14px;border-radius:6px;border:1px solid rgba(255,255,255,0.15);background:rgba(255,255,255,0.08);color:white;font-family:Poppins,sans-serif;font-size:0.85rem;outline:none;">
        <button class="btn btn-sm" type="submit" style="width:100%;">Subscribe Free</button>
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
    <div class="footer-grid">
      <div>
        <div class="footer-brand-name">NicheHub<span>Pro</span></div>
        <p class="footer-brand-desc">Free, science-backed guides on mental wellness, productivity, and healthy living.</p>
      </div>
      <div class="footer-col">
        <h4>Categories</h4>
        <a href="../category.html?cat=mental-wellness">Mental Wellness</a>
        <a href="../category.html?cat=productivity">Productivity</a>
        <a href="../category.html?cat=healthy-lifestyle">Healthy Lifestyle</a>
      </div>
      <div class="footer-col">
        <h4>Company</h4>
        <a href="../about.html">About</a>
        <a href="../contact.html">Contact</a>
        <a href="../privacy.html">Privacy Policy</a>
        <a href="../disclaimer.html">Disclaimer</a>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; 2026 NicheHubPro. All rights reserved.</span>
      <span><a href="../privacy.html">Privacy</a> &nbsp;&middot;&nbsp; <a href="../disclaimer.html">Disclaimer</a></span>
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

    print("Calling Claude API...")
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=8192,
        messages=[
            {
                "role": "user",
                "content": build_user_prompt(primary_kw, secondary_kw, longtail_kw, category)
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

    # Build and save HTML
    print("Building HTML...")
    html = build_html(data, primary_kw, cover_filename)
    out_path = os.path.join(OUT_DIR, f"{article_slug}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Article saved: articles/{article_slug}.html")

    # Register article in articles.js
    register_article(data, cover_filename)

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
        "alt":      data.get("cover_alt_text", data["title"])
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
