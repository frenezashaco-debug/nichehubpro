"""Synchronize catalogue titles and summaries with cleaned article HTML."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / 'articles'
CATALOGUE = ROOT / 'articles.js'
API = ROOT / 'api' / 'articles.json'


def article_details(path: Path) -> tuple[str, str]:
    source = path.read_text(encoding='utf-8')
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', source, re.S | re.I)
    description = re.search(
        r'<meta\b(?=[^>]*\bname=["\']description["\'])[^>]*\bcontent=(["\'])(.*?)\1',
        source,
        re.S | re.I,
    )
    if not h1 or not description:
        raise RuntimeError(f'Missing title or description in {path.name}')
    plain_title = html.unescape(re.sub(r'<[^>]+>', '', h1.group(1))).strip()
    return plain_title, html.unescape(description.group(2)).strip()


def main() -> None:
    details = {path.stem: article_details(path) for path in ARTICLES.glob('*.html')}
    source = CATALOGUE.read_text(encoding='utf-8')
    match = re.search(r'const ARTICLES = (\[[\s\S]*?\]);', source)
    if not match:
        raise RuntimeError('Could not find the ARTICLES catalogue')
    catalogue = json.loads(match.group(1))
    for entry in catalogue:
        if entry['slug'] in details:
            entry['title'], entry['excerpt'] = details[entry['slug']]
    CATALOGUE.write_text(
        source[:match.start(1)] + json.dumps(catalogue, indent=2, ensure_ascii=False) + source[match.end(1):],
        encoding='utf-8',
    )

    api = json.loads(API.read_text(encoding='utf-8'))
    for entry in api:
        if entry['id'] in details:
            entry['title'], entry['shortText'] = details[entry['id']]
    API.write_text(json.dumps(api, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Synchronized {len(details)} article records from cleaned HTML.')


if __name__ == '__main__':
    main()
