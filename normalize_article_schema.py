"""Apply safe, mechanical metadata corrections to every generated article.

This keeps visible FAQs for readers but removes FAQPage structured data, which
must not publish answers that have not received line-by-line editorial review.
It also makes the editorial-team attribution consistent across article pages.
"""

from __future__ import annotations

import re
from pathlib import Path


ARTICLES_DIR = Path(__file__).parent / "articles"
FAQ_SCRIPT = re.compile(
    r'\s*<script type="application/ld\+json">\s*\{\s*"@context":\s*"https://schema\.org",\s*"@type":\s*"FAQPage".*?</script>',
    flags=re.IGNORECASE | re.DOTALL,
)
EDITORIAL_PERSON = re.compile(
    r'"author":\s*\{\s*"@type":\s*"Person",\s*"name":\s*"NicheHubPro Editorial Team"[^}]*\}',
    flags=re.IGNORECASE,
)


def main() -> None:
    changed = 0
    faq_removed = 0
    attribution_fixed = 0
    for path in ARTICLES_DIR.glob("*.html"):
        original = path.read_text(encoding="utf-8")
        updated, removed = FAQ_SCRIPT.subn("", original)
        updated, authors = EDITORIAL_PERSON.subn(
            '"author": { "@type": "Organization", "name": "NicheHubPro Editorial Team", "url": "https://nichehubpro.com/editorial-policy/" }',
            updated,
        )
        updated = updated.replace(
            ">Health &amp; Wellness Writer<", ">Editorial Team<"
        ).replace(
            ">Health & Wellness Writer<", ">Editorial Team<"
        )
        if updated != original:
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed += 1
            faq_removed += removed
            attribution_fixed += authors
    print(f"Updated {changed} article(s): removed {faq_removed} FAQPage schema block(s), fixed {attribution_fixed} author schema value(s).")


if __name__ == "__main__":
    main()
