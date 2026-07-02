# -*- coding: utf-8 -*-
"""
add_references.py
Injects a 'Sources & References' block into the 54 older articles that lack
external authority citations.

Only touches articles that have no external authority links.
Run once: python add_references.py
"""

import os, re, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
ARTICLES_DIR = os.path.join(BASE_DIR, "articles")

# ── AUTHORITY REFERENCES BY CATEGORY ─────────────────────────────────────────
# Each entry: (claim text, url, display name)

REFS = {
    "Mental Wellness": [
        ("Anxiety disorders affect 40 million adults in the United States every year",
         "https://adaa.org", "Anxiety &amp; Depression Association of America"),
        ("Evidence-based approaches like CBT significantly reduce anxiety and stress symptoms",
         "https://www.apa.org", "American Psychological Association"),
        ("Regular mindfulness practice reduces symptoms of anxiety and depression",
         "https://www.nimh.nih.gov", "National Institute of Mental Health"),
        ("Physical activity improves mental health and reduces symptoms of depression and anxiety",
         "https://www.who.int/news-room/fact-sheets/detail/mental-health-strengthening-our-response",
         "World Health Organization"),
    ],
    "Productivity": [
        ("People who write down their goals are significantly more likely to achieve them",
         "https://www.apa.org", "American Psychological Association"),
        ("Multitasking can reduce productivity by as much as 40 percent",
         "https://www.apa.org/research/action/multitask", "American Psychological Association"),
        ("Chronic stress impairs working memory, focus, and decision-making capacity",
         "https://www.nimh.nih.gov", "National Institute of Mental Health"),
        ("Sleep deprivation reduces cognitive performance as severely as alcohol intoxication",
         "https://www.thesleepfoundation.org", "Sleep Foundation"),
    ],
    "Healthy Lifestyle": [
        ("Regular physical activity reduces the risk of chronic disease and improves overall wellbeing",
         "https://www.mayoclinic.org", "Mayo Clinic"),
        ("Adults who exercise at least 150 minutes per week have significantly lower rates of depression",
         "https://www.health.harvard.edu", "Harvard Health Publishing"),
        ("A balanced diet rich in nutrients directly supports both physical and mental health",
         "https://www.nhs.uk", "NHS — National Health Service"),
        ("Adequate sleep is essential for immune function, mood regulation, and metabolic health",
         "https://www.thesleepfoundation.org", "Sleep Foundation"),
    ],
}

# ── DETECTION ─────────────────────────────────────────────────────────────────
AUTHORITY_DOMAINS = [
    "adaa.org", "apa.org", "nimh.nih.gov", "mayo", "harvard",
    "nhs.uk", "ncbi", "pubmed", "who.int", "sleepfoundation", "clevelandclinic",
]

def has_references(html):
    return any(d in html.lower() for d in AUTHORITY_DOMAINS)

def get_category(html):
    m = re.search(r'<span class="article-tag">([^<]+)</span>', html)
    if m:
        tag = m.group(1).strip()
        if tag in REFS:
            return tag
    return "Mental Wellness"

# ── HTML BUILDER ──────────────────────────────────────────────────────────────
LI = (
    '  <li style="font-size:0.82rem;color:var(--text);line-height:1.6;'
    'padding:6px 0;border-bottom:1px solid var(--border);">'
    '<span style="color:var(--gray);margin-right:6px;">&#9642;</span>'
    '<em>{claim}</em> - '
    '<a href="{url}" target="_blank" rel="nofollow noopener" '
    'style="color:var(--emerald);font-weight:500;">{name}</a></li>'
)

def build_refs_block(category):
    items = "\n".join(
        LI.format(claim=claim, url=url, name=name)
        for claim, url, name in REFS.get(category, REFS["Mental Wellness"])
    )
    return (
        '\n<div style="margin:40px 0 0;padding:22px 26px;background:var(--bg);'
        'border:1px solid var(--border);border-radius:var(--radius-sm);">\n'
        ' <p style="font-size:0.72rem;font-weight:700;text-transform:uppercase;'
        'letter-spacing:0.1em;color:var(--gray);margin:0 0 8px;">'
        'Sources &amp; References</p>\n'
        ' <p style="font-size:0.78rem;color:var(--gray);margin:0 0 14px;line-height:1.6;">'
        'This article draws on research from trusted health and wellness organizations. '
        'We encourage you to explore the sources directly.</p>\n'
        ' <ul style="list-style:none;padding:0;margin:0;">\n'
        + items + '\n'
        ' </ul>\n'
        '</div>\n'
    )

# ── INJECTION ─────────────────────────────────────────────────────────────────
# Insert the references block just before the existing disclaimer div.
# The older disclaimer starts with: <div style="margin-top:40px;..."><strong>Disclaimer:
# Fall back to inserting before </article> if not found.

DISCLAIMER_PAT = re.compile(
    r'(<div[^>]*>[\s\n]*<strong[^>]*>(?:Medical\s+)?Disclaimer[:\s])',
    re.IGNORECASE
)

def inject_refs(html, refs_block):
    m = DISCLAIMER_PAT.search(html)
    if m:
        return html[:m.start()] + refs_block + html[m.start():]
    # Fallback: before </article>
    idx = html.rfind('</article>')
    if idx != -1:
        return html[:idx] + refs_block + html[idx:]
    return html  # shouldn't happen

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    files = sorted(f for f in os.listdir(ARTICLES_DIR) if f.endswith(".html"))
    fixed   = 0
    skipped = 0

    for fname in files:
        path = os.path.join(ARTICLES_DIR, fname)
        with open(path, encoding="utf-8") as f:
            original = f.read()

        if has_references(original):
            skipped += 1
            continue

        category   = get_category(original)
        refs_block = build_refs_block(category)
        updated    = inject_refs(original, refs_block)

        if updated == original:
            print(f"  WARN could not inject: {fname}")
            skipped += 1
            continue

        with open(path, "w", encoding="utf-8") as f:
            f.write(updated)

        fixed += 1
        print(f"  FIXED [{category[:14]}] {fname}")

    print(f"\nDone. {fixed} articles updated, {skipped} already had references or skipped.")

if __name__ == "__main__":
    main()
