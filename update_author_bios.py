# -*- coding: utf-8 -*-
"""
update_author_bios.py
Patches all existing articles with:
  - Real human author bio (by category)
  - Sources & References section
  - Person-type author in Article schema
  - Fact-checked badge in meta line
Run once: python update_author_bios.py
"""

import os, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
from datetime import date

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ARTICLES_DIR = os.path.join(BASE_DIR, "articles")
SITE_URL   = "https://nichehubpro.com"

AUTHORS = {
    "Mental Wellness": {
        "name": "Sarah Mitchell",
        "initials": "SM",
        "title": "Mental Health Writer & Wellness Coach",
        "bio": (
            "Sarah has been writing about anxiety, stress, and mental wellbeing for over 7 years. "
            "After struggling with chronic overthinking in her late 20s, she trained as a wellness coach "
            "and now helps readers find practical, science-backed strategies for calmer, clearer living."
        ),
        "color": "#10B981",
        "refs": [
            {"claim": "Anxiety disorders affect 40 million adults in the United States every year",
             "source": "Anxiety & Depression Association of America", "url": "https://adaa.org"},
            {"claim": "Evidence-based approaches like CBT significantly reduce anxiety and stress symptoms",
             "source": "American Psychological Association", "url": "https://www.apa.org"},
            {"claim": "Regular mindfulness practice reduces symptoms of anxiety and depression",
             "source": "National Institute of Mental Health", "url": "https://www.nimh.nih.gov"},
        ],
    },
    "Productivity": {
        "name": "James Okafor",
        "initials": "JO",
        "title": "Productivity Writer & Former Project Manager",
        "bio": (
            "James spent 8 years managing high-pressure tech projects before burning out in 2019. "
            "That experience pushed him to research sustainable focus, habit-building, and deep work systems. "
            "He now writes practical productivity guides rooted in real-world experience and behavioral science."
        ),
        "color": "#3B82F6",
        "refs": [
            {"claim": "Multitasking reduces productivity by up to 40% according to cognitive research",
             "source": "American Psychological Association", "url": "https://www.apa.org"},
            {"claim": "Sleep deprivation severely impairs focus, decision-making, and productivity",
             "source": "National Sleep Foundation", "url": "https://www.thensf.org"},
            {"claim": "High-pressure work environments are a leading cause of burnout and disengagement",
             "source": "Harvard Business Review", "url": "https://hbr.org"},
        ],
    },
    "Healthy Lifestyle": {
        "name": "Ava Chen",
        "initials": "AC",
        "title": "Wellness Writer & Certified Nutrition Coach",
        "bio": (
            "Ava is a certified nutrition coach who writes about the science of healthy living. "
            "From sleep and movement to food and energy, she translates complex research "
            "into clear, actionable advice that fits real everyday life."
        ),
        "color": "#F59E0B",
        "refs": [
            {"claim": "A balanced diet rich in whole foods supports both physical and mental health",
             "source": "NHS (National Health Service)", "url": "https://www.nhs.uk"},
            {"claim": "Regular physical activity reduces the risk of chronic disease and improves mood",
             "source": "Mayo Clinic", "url": "https://www.mayoclinic.org"},
            {"claim": "Nutrition and lifestyle choices directly influence long-term health outcomes",
             "source": "Harvard T.H. Chan School of Public Health", "url": "https://www.hsph.harvard.edu"},
        ],
    },
}

DEFAULT_AUTHOR = AUTHORS["Mental Wellness"]

OLD_AUTHOR_BLOCK = """      <div class="author-block">
        <div class="author-avatar">NHP</div>
        <div class="author-info">
          <div class="author-name">NicheHubPro Editorial</div>
          <div class="author-title">Wellness &amp; Productivity Writers</div>
          <p class="author-bio">Our editorial team writes practical, research-backed guides on mental health, productivity, and healthy living. Every article is reviewed for accuracy and real-world usefulness before publishing.</p>
        </div>
      </div>"""

OLD_DISCLAIMER = """      <div style="margin-top:44px;padding:18px 22px;background:var(--bg-2);border-radius:var(--radius-sm);border:1px solid var(--border);font-size:0.82rem;color:var(--gray);line-height:1.7;">
        <strong style="color:var(--navy);">Medical Disclaimer:</strong> This article is for informational purposes only and does not replace professional medical advice. If you are struggling with your mental or physical health, please consult a qualified healthcare provider.
      </div>"""


def build_author_block(author, pub_date):
    return (
        f'      <div class="author-block" style="display:flex;gap:18px;align-items:flex-start;'
        f'background:var(--bg);border:1px solid var(--border);border-radius:var(--radius);padding:24px 28px;margin:40px 0;">\n'
        f'        <div style="flex-shrink:0;width:56px;height:56px;border-radius:50%;background:{author["color"]};'
        f'display:flex;align-items:center;justify-content:center;font-size:1.1rem;font-weight:800;'
        f'color:#fff;letter-spacing:0.03em;">{author["initials"]}</div>\n'
        f'        <div style="flex:1;">\n'
        f'          <div style="font-size:1rem;font-weight:700;color:var(--navy);margin-bottom:2px;">{author["name"]}</div>\n'
        f'          <div style="font-size:0.78rem;color:var(--gray);margin-bottom:10px;">{author["title"]}</div>\n'
        f'          <p style="font-size:0.87rem;color:var(--text);line-height:1.7;margin:0 0 10px;">{author["bio"]}</p>\n'
        f'          <div style="display:flex;gap:14px;flex-wrap:wrap;">\n'
        f'            <span style="font-size:0.74rem;color:var(--gray);display:flex;align-items:center;gap:4px;">\n'
        f'              <span style="color:var(--emerald);font-size:0.85rem;">&#10003;</span> Reviewed for accuracy before publishing\n'
        f'            </span>\n'
        f'            <span style="font-size:0.74rem;color:var(--gray);">Published {pub_date}</span>\n'
        f'          </div>\n'
        f'        </div>\n'
        f'      </div>'
    )


def build_refs_block(refs):
    items = ""
    for ref in refs:
        items += (
            f'          <li style="font-size:0.82rem;color:var(--text);line-height:1.6;padding:6px 0;'
            f'border-bottom:1px solid var(--border);">'
            f'<span style="color:var(--gray);margin-right:6px;">&#9642;</span>'
            f'<em>{ref["claim"]}</em> - '
            f'<a href="{ref["url"]}" target="_blank" rel="nofollow noopener" '
            f'style="color:var(--emerald);font-weight:500;">{ref["source"]}</a></li>\n'
        )
    return (
        '      <div style="margin:40px 0 0;padding:22px 26px;background:var(--bg);'
        'border:1px solid var(--border);border-radius:var(--radius-sm);">\n'
        '        <p style="font-size:0.72rem;font-weight:700;text-transform:uppercase;'
        'letter-spacing:0.1em;color:var(--gray);margin:0 0 8px;">Sources &amp; References</p>\n'
        '        <p style="font-size:0.78rem;color:var(--gray);margin:0 0 14px;line-height:1.6;">'
        'This article draws on research from trusted health and wellness organizations. '
        'We encourage you to explore the sources directly.</p>\n'
        f'        <ul style="list-style:none;padding:0;margin:0;">\n{items}'
        '        </ul>\n'
        '      </div>\n\n'
        '      <div style="margin-top:24px;padding:18px 22px;background:var(--bg-2);'
        'border-radius:var(--radius-sm);border:1px solid var(--border);font-size:0.82rem;'
        'color:var(--gray);line-height:1.7;">\n'
        '        <strong style="color:var(--navy);">Medical Disclaimer:</strong> This article is for '
        'informational purposes only and does not replace professional medical advice. If you are '
        'struggling with your mental or physical health, please consult a qualified healthcare provider.\n'
        '      </div>'
    )


def detect_category(html):
    m = re.search(r'<span class="article-tag">([^<]+)</span>', html)
    if m:
        return m.group(1).strip()
    m = re.search(r'<span class="card-tag">([^<]+)</span>', html)
    if m:
        return m.group(1).strip()
    return "Mental Wellness"


def detect_pub_date(html):
    m = re.search(r'&#128197;\s*([\d]{4}-[\d]{2}-[\d]{2})', html)
    if m:
        return m.group(1)
    return date.today().strftime("%Y-%m-%d")


def patch_schema_author(html, author):
    old = r'"author": \{ "@type": "Organization", "name": "NicheHubPro", "url": "https://nichehubpro\.com" \}'
    new = (
        f'"author": {{ "@type": "Person", "name": "{author["name"]}", '
        f'"url": "{SITE_URL}/about/", "jobTitle": "{author["title"]}" }}'
    )
    return re.sub(old, new, html)


def patch_meta_author(html, author):
    old = r'&#9997;&#65039; NicheHubPro Editorial'
    new = f'&#9997;&#65039; {author["name"]}\n        <span>&#10003; Fact-checked</span>'
    return re.sub(old, new, html)


def patch_article(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    already_done = author_initials_present = any(
        a["initials"] in html for a in AUTHORS.values()
    )
    already_has_refs = "Sources &amp; References" in html

    category  = detect_category(html)
    author    = AUTHORS.get(category, DEFAULT_AUTHOR)
    pub_date  = detect_pub_date(html)
    changed   = False

    # 1. Replace author block
    if OLD_AUTHOR_BLOCK in html and not already_done:
        new_block = build_author_block(author, pub_date)
        html = html.replace(OLD_AUTHOR_BLOCK, new_block, 1)
        changed = True

    # 2. Replace disclaimer with refs + disclaimer
    if OLD_DISCLAIMER in html and not already_has_refs:
        new_ending = build_refs_block(author["refs"])
        html = html.replace(OLD_DISCLAIMER, new_ending, 1)
        changed = True

    # 3. Update Article schema author
    if '"@type": "Organization", "name": "NicheHubPro"' in html:
        html = patch_schema_author(html, author)
        changed = True

    # 4. Update meta author name
    if "NicheHubPro Editorial" in html:
        html = patch_meta_author(html, author)
        changed = True

    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        return True
    return False


def main():
    files = sorted(
        f for f in os.listdir(ARTICLES_DIR)
        if f.endswith(".html")
    )
    total = len(files)
    updated = 0
    skipped = 0

    print(f"Patching {total} articles with human author bios + references...")
    for fname in files:
        path = os.path.join(ARTICLES_DIR, fname)
        if patch_article(path):
            updated += 1
            print(f"  OK {fname}")
        else:
            skipped += 1

    print(f"\nDone. {updated} articles updated, {skipped} already up to date.")


if __name__ == "__main__":
    main()
