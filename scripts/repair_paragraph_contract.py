"""Split reader paragraphs that exceed the publication length contract."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARAGRAPH = re.compile(r'(<p\b[^>]*>)(.*?)(</p>)', re.S | re.I)


def word_count(markup: str) -> int:
    return len(re.sub(r'<[^>]+>', ' ', markup).split())


def split_paragraph(match: re.Match) -> str:
    opening, content, closing = match.groups()
    if word_count(content) <= 60:
        return match.group(0)
    sentences = re.split(r'(?<=[.!?])\s+', content)
    midpoint = max(1, len(sentences) // 2)
    left = ' '.join(sentences[:midpoint]).strip()
    right = ' '.join(sentences[midpoint:]).strip()
    if not left or not right or word_count(left) > 60 or word_count(right) > 60:
        raise RuntimeError('Could not safely split an overlong paragraph')
    return opening + left + closing + '\n' + opening + right + closing


def main() -> None:
    updated = 0
    for path in ROOT.joinpath('articles').glob('*.html'):
        source = path.read_text(encoding='utf-8')
        cleaned = PARAGRAPH.sub(split_paragraph, source)
        if cleaned != source:
            path.write_text(cleaned, encoding='utf-8')
            updated += 1
    print(f'Repaired paragraph length in {updated} article files.')


if __name__ == '__main__':
    main()
