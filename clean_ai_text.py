# -*- coding: utf-8 -*-
"""
clean_ai_text.py
Normalizes forbidden dash forms and the explicitly prohibited style phrases.
Does not identify AI authorship, image watermarks, or scientific accuracy.
Run once: python clean_ai_text.py
Also imported by publisher_v2.py to clean new articles on generation.
"""

import json, os, re, sys
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
_FORBIDDEN_DASH = re.compile(r'[\u2010-\u2015]|&(?:mdash|ndash);|&#(?:8208|8209|8210|8211|8212|8213);|&#x(?:2010|2011|2012|2013|2014|2015);', re.I)
_WORD_HYPHEN = re.compile(r'(?<=[A-Za-z])[-\u2010-\u2015](?=[A-Za-z])')
_JSON_LD = re.compile(
    r'(<script\b[^>]*\btype=["\']application/ld\+json["\'][^>]*>)([\s\S]*?)(</script>)',
    re.I,
)
_TEXT_JSON_KEYS = {'headline', 'description', 'text', 'name', 'articleBody', 'abstract'}
_DESCRIPTION_META = re.compile(
    r'<meta\b(?=[^>]*\b(?:name|property)=["\'](?:description|og:description)["\'])[^>]*>',
    re.I,
)
_CONTENT_ATTRIBUTE = re.compile(r'(\bcontent=)(["\'])(.*?)(\2)', re.I)


def _text_parts(markup: str) -> list[str]:
    """Split markup while leaving tags, scripts, and styles untouched."""
    return re.split(r'(<script\b[^>]*>[\s\S]*?</script>|<style\b[^>]*>[\s\S]*?</style>|<[^>]+>)', markup, flags=re.I)


def _clean_copy(value: str) -> str:
    value = _FORBIDDEN_DASH.sub(' ', value)
    value = _WORD_HYPHEN.sub(' ', value)
    for pattern, replacement in _COPY_RULES:
        value = pattern.sub(replacement, value)
    return value


def _clean_json_ld_value(value, key=''):
    if isinstance(value, str):
        return _clean_copy(value) if key in _TEXT_JSON_KEYS else value
    if isinstance(value, list):
        return [_clean_json_ld_value(item, key) for item in value]
    if isinstance(value, dict):
        return {item_key: _clean_json_ld_value(item_value, item_key) for item_key, item_value in value.items()}
    return value


def _clean_json_ld(match):
    try:
        data = json.loads(match.group(2))
    except json.JSONDecodeError:
        return match.group(0)
    cleaned = _clean_json_ld_value(data)
    return match.group(1) + '\n' + json.dumps(cleaned, ensure_ascii=False, indent=2) + '\n' + match.group(3)


def _clean_description_meta(match):
    tag = match.group(0)
    return _CONTENT_ATTRIBUTE.sub(
        lambda attribute: attribute.group(1) + attribute.group(2) + _clean_copy(attribute.group(3)) + attribute.group(4),
        tag,
        count=1,
    )


def clean_ai_text(html: str) -> str:
    """Preserve links, styles, and structured data while cleaning visible copy."""
    parts = _text_parts(html)
    for index in range(0, len(parts), 2):
        parts[index] = _clean_copy(parts[index])
    cleaned = _JSON_LD.sub(_clean_json_ld, ''.join(parts))
    return _DESCRIPTION_META.sub(_clean_description_meta, cleaned)


def visible_word_hyphens(markup: str) -> int:
    """Count hyphens in reader-facing text without inspecting URLs or code."""
    return sum(len(_WORD_HYPHEN.findall(part)) for part in _text_parts(markup)[::2])


def main():
    files = sorted(f for f in os.listdir(ARTICLES_DIR) if f.endswith(".html"))
    total   = len(files)
    updated = 0
    remaining = 0

    print(f"Normalizing explicit style rules in {total} articles...")
    for fname in files:
        path = os.path.join(ARTICLES_DIR, fname)
        with open(path, encoding="utf-8") as f:
            original = f.read()
        cleaned = clean_ai_text(original)
        remaining += visible_word_hyphens(cleaned)
        if cleaned != original:
            with open(path, "w", encoding="utf-8") as f:
                f.write(cleaned)
            updated += 1
            print(f"  FIXED {fname}")

    print(f"\nDone. {updated}/{total} articles cleaned. Visible word hyphens remaining: {remaining}.")


if __name__ == "__main__":
    main()
