"""Find existing article claims that need a direct, reviewable source.

This does not decide whether a claim is true. It highlights wording that should
be checked by an editor before an article is relied on for health, wellbeing, or
productivity guidance.
"""

from __future__ import annotations

import html
import re
import sys
from collections import Counter
from pathlib import Path


ARTICLES_DIR = Path(__file__).parent / "articles"
sys.stdout.reconfigure(encoding="utf-8")
PATTERNS = {
    "precise percentage": re.compile(r"\b\d{1,3}%\b", re.I),
    "named study or journal": re.compile(r"\b(?:study|studies|research)\b.{0,80}\b(?:journal|university|researchers?)\b|\bJournal of\b", re.I),
    "unlinked evidence claim": re.compile(r"\b(?:studies?|research)\s+(?:show|shows|found|finds|proves)\b", re.I),
    "medical certainty": re.compile(r"\b(?:cures?|reverses?|guarantees?)\b", re.I),
}


def visible_text(markup: str) -> str:
    markup = re.sub(r"<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>", " ", markup, flags=re.I | re.S)
    return html.unescape(re.sub(r"<[^>]+>", " ", markup))


def sentences(text: str):
    return re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text))


def main() -> None:
    findings = []
    counts = Counter()
    for path in sorted(ARTICLES_DIR.glob("*.html")):
        for sentence in sentences(visible_text(path.read_text(encoding="utf-8"))):
            for label, pattern in PATTERNS.items():
                if pattern.search(sentence):
                    findings.append((path.name, label, sentence[:240]))
                    counts[label] += 1

    print(f"Flagged {len(findings)} candidate claims across {len(list(ARTICLES_DIR.glob('*.html')))} articles.")
    for label, count in counts.most_common():
        print(f"- {label}: {count}")
    print("\nFirst 40 items for manual review:")
    for file_name, label, sentence in findings[:40]:
        print(f"[{label}] {file_name}: {sentence}")


if __name__ == "__main__":
    main()
