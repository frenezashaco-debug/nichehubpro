# -*- coding: utf-8 -*-
"""
clean_ai_text.py
Normalizes forbidden dash forms and the explicitly prohibited style phrases.
Does not identify AI authorship, image watermarks, or scientific accuracy.
Run once: python clean_ai_text.py
Also imported by publisher_v2.py to clean new articles on generation.
"""

import os, re, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
ARTICLES_DIR = os.path.join(BASE_DIR, "articles")

# Keep changes limited to explicit project style rules.
_COPY_RULES = [
    (re.compile(r'\bdelves?\b', re.I), 'explores'),
    (re.compile(r'\bdelved\b', re.I), 'explored'),
    (re.compile(r'\bdelving\b', re.I), 'exploring'),
    (re.compile(r"\bIn today's fast-paced world,?\s*", re.I), ''),
    (re.compile(r'\bIt is important to note(?: that)?\s*', re.I), ''),
    (re.compile(r'\bIn conclusion,?\s*', re.I), ''),
]
_FORBIDDEN_DASH = re.compile(r'[\u2013\u2014\u2015]|&(?:mdash|ndash);|&#(?:8211|8212|8213);|&#x(?:2013|2014|2015);', re.I)


def clean_ai_text(html: str) -> str:
    """Preserve scientific wording, links, styles and structured data."""
    html = _FORBIDDEN_DASH.sub('-', html)
    parts = re.split(r'(<script\b[^>]*>[\s\S]*?</script>|<style\b[^>]*>[\s\S]*?</style>|<[^>]+>)', html, flags=re.I)
    for index in range(0, len(parts), 2):
        for pattern, replacement in _COPY_RULES:
            parts[index] = pattern.sub(replacement, parts[index])
    return ''.join(parts)


def main():
    files = sorted(f for f in os.listdir(ARTICLES_DIR) if f.endswith(".html"))
    total   = len(files)
    updated = 0

    print(f"Normalizing explicit style rules in {total} articles...")
    for fname in files:
        path = os.path.join(ARTICLES_DIR, fname)
        with open(path, encoding="utf-8") as f:
            original = f.read()
        cleaned = clean_ai_text(original)
        if cleaned != original:
            with open(path, "w", encoding="utf-8") as f:
                f.write(cleaned)
            updated += 1
            print(f"  FIXED {fname}")

    print(f"\nDone. {updated}/{total} articles cleaned.")


if __name__ == "__main__":
    main()
