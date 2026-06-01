# -*- coding: utf-8 -*-
"""
clean_ai_text.py
Strips AI watermark words, em dashes, and robotic phrasing from all articles.
Run once: python clean_ai_text.py
Also imported by publisher_v2.py to clean new articles on generation.
"""

import os, re, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
ARTICLES_DIR = os.path.join(BASE_DIR, "articles")

# ── SIMPLE STRING REPLACEMENTS (applied in order) ────────────────────────────
# Em dash / en dash — ALL forms
_SIMPLE = [
    # HTML entities first
    (" &mdash; ",  " - "),
    ("&mdash;",    " - "),
    (" &ndash; ",  " - "),
    ("&ndash;",    " - "),
    (" &#8212; ",  " - "),
    ("&#8212;",    " - "),
    (" &#8211; ",  " - "),
    ("&#8211;",    " - "),
    # Unicode characters
    (" — ",   " - "),
    ("—",     " - "),
    (" – ",   " - "),
    ("–",     " - "),
    (" ― ",   " - "),
    ("―",     " - "),
    # Leftover double-space from removals
    ("  ",         " "),
]

# ── REGEX REPLACEMENTS (word-boundary safe, HTML-aware) ──────────────────────
# Only replaces inside visible text — patterns chosen to not match HTML tags.
# Format: (compiled_pattern, replacement_string_or_callable)
_REGEX = [
    # Absolute AI bans (from CLAUDE.md rules)
    (re.compile(r'\bdelves?\b', re.I),                         "explores"),
    (re.compile(r'\bdelved\b', re.I),                          "explored"),
    (re.compile(r'\bdelving\b', re.I),                         "exploring"),
    (re.compile(r"in today'?s fast-?paced world,?\s*", re.I),  ""),
    (re.compile(r"in today'?s world,?\s*", re.I),              "today, "),
    (re.compile(r"it is important to note that\b", re.I),      "keep in mind:"),
    (re.compile(r"it'?s important to note that\b", re.I),      "keep in mind:"),
    (re.compile(r"it is important to note\b", re.I),           "keep in mind:"),
    (re.compile(r"it'?s worth noting that\b", re.I),           "note that"),
    (re.compile(r"it'?s worth noting\b", re.I),                "note:"),
    (re.compile(r"\bIn conclusion,?\s*", re.I),                ""),
    (re.compile(r"\bTo summarize,?\s*", re.I),                 ""),
    (re.compile(r"\bIn summary,?\s*", re.I),                   ""),

    # Robotic sentence starters — replace with natural alternatives
    (re.compile(r"\bFurthermore,\s*", re.I),                   "Also, "),
    (re.compile(r"\bMoreover,\s*", re.I),                      "Also, "),
    (re.compile(r"\bAdditionally,\s*", re.I),                  "Also, "),
    (re.compile(r"\bConsequently,\s*", re.I),                  "As a result, "),
    (re.compile(r"\bSubsequently,\s*", re.I),                  "After that, "),
    (re.compile(r"\bNevertheless,\s*", re.I),                  "Still, "),
    (re.compile(r"\bNotwithstanding,\s*", re.I),               "Even so, "),
    (re.compile(r"\bHenceforth,\s*", re.I),                    "From now on, "),
    (re.compile(r"\bHerein\b", re.I),                          "here"),
    (re.compile(r"\bTherefore,\s*", re.I),                     "So, "),
    (re.compile(r"\bThus,\s*", re.I),                          "So, "),
    (re.compile(r"\bHence,\s*", re.I),                         "So, "),

    # Forbidden AI buzzwords — swap to natural language
    (re.compile(r"\butilize\b", re.I),                         "use"),
    (re.compile(r"\butilizes\b", re.I),                        "uses"),
    (re.compile(r"\butilized\b", re.I),                        "used"),
    (re.compile(r"\butilizing\b", re.I),                       "using"),
    (re.compile(r"\butilisation\b", re.I),                     "use"),
    (re.compile(r"\butilization\b", re.I),                     "use"),
    (re.compile(r"\bfacilitate\b", re.I),                      "help"),
    (re.compile(r"\bfacilitates\b", re.I),                     "helps"),
    (re.compile(r"\bfacilitated\b", re.I),                     "helped"),
    (re.compile(r"\bfacilitating\b", re.I),                    "helping"),
    (re.compile(r"\bpivotal\b", re.I),                         "key"),
    (re.compile(r"\bcrucial\b", re.I),                         "important"),
    (re.compile(r"\bcrucially\b", re.I),                       "importantly"),
    (re.compile(r"\bcomprehensive\b", re.I),                   "complete"),
    (re.compile(r"\bcomprehensively\b", re.I),                 "fully"),
    (re.compile(r"\bmultifaceted\b", re.I),                    "complex"),
    (re.compile(r"\bnuanced\b", re.I),                         "subtle"),
    (re.compile(r"\bparadigm shift\b", re.I),                  "big change"),
    (re.compile(r"\bparadigm\b", re.I),                        "model"),
    (re.compile(r"\bsynergy\b", re.I),                         "combination"),
    (re.compile(r"\bsynergies\b", re.I),                       "combinations"),
    (re.compile(r"\bsynergistic\b", re.I),                     "combined"),
    (re.compile(r"\bstreamline\b", re.I),                      "simplify"),
    (re.compile(r"\bstreamlines\b", re.I),                     "simplifies"),
    (re.compile(r"\bstreamlined\b", re.I),                     "simplified"),
    (re.compile(r"\bstreamlining\b", re.I),                    "simplifying"),
    (re.compile(r"\bseamlessly\b", re.I),                      "easily"),
    (re.compile(r"\bseamless\b", re.I),                        "smooth"),
    (re.compile(r"\binvaluable\b", re.I),                      "very useful"),
    (re.compile(r"\bembark on\b", re.I),                       "start"),
    (re.compile(r"\bembark upon\b", re.I),                     "start"),
    (re.compile(r"\bembark\b", re.I),                          "start"),
    (re.compile(r"\btapestry\b", re.I),                        "mix"),
    (re.compile(r"\bholistic approach\b", re.I),               "full approach"),
    (re.compile(r"\bholistically\b", re.I),                    "fully"),
    (re.compile(r"\boptimize\b", re.I),                        "improve"),
    (re.compile(r"\boptimises?\b", re.I),                      "improves"),
    (re.compile(r"\boptimized\b", re.I),                       "improved"),
    (re.compile(r"\boptimizing\b", re.I),                      "improving"),
    (re.compile(r"\boptimisation\b", re.I),                    "improvement"),
    (re.compile(r"\brobust\b", re.I),                          "strong"),
    (re.compile(r"\bpropel\b", re.I),                          "push"),
    (re.compile(r"\bpropels\b", re.I),                         "pushes"),
    (re.compile(r"\bcurated\b", re.I),                         "selected"),
    (re.compile(r"\bempowering you to\b", re.I),               "helping you"),
    (re.compile(r"\bempowers? you\b", re.I),                   "helps you"),
    (re.compile(r"\bempower\b", re.I),                         "help"),
    (re.compile(r"\bempowers\b", re.I),                        "helps"),
    (re.compile(r"\bempowering\b", re.I),                      "helping"),
    (re.compile(r"\bunlock(?:s|ed|ing)? (?:your )?potential\b", re.I), "reach your potential"),
    (re.compile(r"\bleverage\b", re.I),                        "use"),
    (re.compile(r"\bleverages\b", re.I),                       "uses"),
    (re.compile(r"\bleveraged\b", re.I),                       "used"),
    (re.compile(r"\bleveraging\b", re.I),                      "using"),
    (re.compile(r"\belevate\b", re.I),                         "improve"),
    (re.compile(r"\belevates\b", re.I),                        "improves"),
    (re.compile(r"\belevated\b", re.I),                        "improved"),
    (re.compile(r"\belevating\b", re.I),                       "improving"),
    (re.compile(r"\bgame-changer\b", re.I),                    "big help"),
    (re.compile(r"\bgame changer\b", re.I),                    "big help"),
    (re.compile(r"\bgame-changing\b", re.I),                   "transformative"),
    (re.compile(r"\btailored to\b", re.I),                     "made for"),
    (re.compile(r"\bunleash\b", re.I),                         "release"),
    (re.compile(r"\bunleashes\b", re.I),                       "releases"),
    (re.compile(r"\bnavigate\b", re.I),                        "handle"),
    (re.compile(r"\bnavigates\b", re.I),                       "handles"),
    (re.compile(r"\bnavigated\b", re.I),                       "handled"),
    (re.compile(r"\bnavigating\b", re.I),                      "handling"),
    (re.compile(r"\bfoster\b", re.I),                          "build"),
    (re.compile(r"\bfosters\b", re.I),                         "builds"),
    (re.compile(r"\bfostered\b", re.I),                        "built"),
    (re.compile(r"\bfostering\b", re.I),                       "building"),
    (re.compile(r"\bbreakthrough\b", re.I),                    "discovery"),
    (re.compile(r"\bgroundbreaking\b", re.I),                  "new"),
    (re.compile(r"\bcutting-edge\b", re.I),                    "modern"),
    (re.compile(r"\bstate-of-the-art\b", re.I),               "modern"),
    (re.compile(r"\bpathway to\b", re.I),                      "path to"),
    (re.compile(r"\bpathways? forward\b", re.I),               "way forward"),
    (re.compile(r"\bin the realm of\b", re.I),                 "in"),
    (re.compile(r"\bIn the world of\b", re.I),                 "In"),
    (re.compile(r"\bwhen it comes to\b", re.I),                "for"),
    (re.compile(r"\bit'?s crucial that\b", re.I),              "make sure"),
    (re.compile(r"\bit is crucial that\b", re.I),              "make sure"),
    (re.compile(r"\bone must\b", re.I),                        "you should"),
    (re.compile(r"\bone should\b", re.I),                      "you should"),
    (re.compile(r"\bone can\b", re.I),                         "you can"),
    (re.compile(r"\bissue at hand\b", re.I),                   "issue"),
    (re.compile(r"\bmatters at hand\b", re.I),                 "matters"),
    (re.compile(r"\bmyriad of\b", re.I),                       "many"),
    (re.compile(r"\bplethora of\b", re.I),                     "many"),
    (re.compile(r"\ba wide array of\b", re.I),                 "many"),
    (re.compile(r"\ba variety of\b", re.I),                    "many"),
    (re.compile(r"\ba wide range of\b", re.I),                 "many"),
    (re.compile(r"\bindeed\b", re.I),                          ""),
    (re.compile(r"\bultimately\b", re.I),                      "in the end"),
    (re.compile(r"\bsignificantly\b", re.I),                   "greatly"),
    (re.compile(r"\bsubstantially\b", re.I),                   "greatly"),
    (re.compile(r"\bconsiderable\b", re.I),                    "large"),
    (re.compile(r"\bconsiderably\b", re.I),                    "greatly"),
]

# Patterns that should ONLY be replaced outside of HTML tags
_IN_TAG = re.compile(r'<[^>]+>')


def clean_ai_text(html: str) -> str:
    """Apply all AI watermark removals to article HTML."""
    # Simple string replacements (safe for full HTML)
    for old, new in _SIMPLE:
        html = html.replace(old, new)

    # Regex replacements — only apply inside text nodes, not inside HTML tags
    # Strategy: split on tags, replace in text segments only
    parts = _IN_TAG.split(html)
    tags  = _IN_TAG.findall(html)

    cleaned_parts = []
    for part in parts:
        for pattern, replacement in _REGEX:
            part = pattern.sub(replacement, part)
        # Clean double spaces left by removals
        part = re.sub(r'  +', ' ', part)
        cleaned_parts.append(part)

    # Interleave parts and tags back together
    result = cleaned_parts[0]
    for tag, part in zip(tags, cleaned_parts[1:]):
        result += tag + part

    return result


def main():
    files = sorted(f for f in os.listdir(ARTICLES_DIR) if f.endswith(".html"))
    total   = len(files)
    updated = 0

    print(f"Cleaning AI watermarks from {total} articles...")
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
