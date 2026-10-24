"""Focused verification of the healthy-lifestyle-tips editorial revision."""
import html
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
source = (root / 'articles/healthy-lifestyle-tips.html').read_text(encoding='utf-8')
documents = [json.loads(raw) for raw in re.findall(
    r'<script type="application/ld\+json">(.*?)</script>', source, re.S)]
faq = next(item for item in documents if item.get('@type') == 'FAQPage')
answers = re.findall(r'<div class="faq-a">(.*?)</div>', source, re.S)
assert len(answers) == 5
assert [item['acceptedAnswer']['text'] for item in faq['mainEntity']] == answers
assert '\u2014' not in source
meta = re.search(r'<meta name="description" content="([^"]+)"', source).group(1)
assert 155 <= len(meta) <= 160, len(meta)
body = source.split('<article class="article-content" id="article-body">')[1]
main = body.split('<h2>An Illustrative Scenario</h2>')[0]
headings = re.findall(r'<h2>(.*?)</h2>', main)
assert len(headings) == 5 and all(item.endswith('?') for item in headings)
links = re.findall(r'href="(/articles/[^"#]+)"', main)
assert len(links) == 3 and len(set(links)) == 3
assert len(re.findall(r'<img ', body)) == 3
assert 'This article is for informational purposes only and does not replace professional medical advice.' in source
for path in links:
    assert (root / path.lstrip('/')).is_file(), path
for paragraph in re.findall(r'<p(?: [^>]*)?>(.*?)</p>', source, re.S):
    words = html.unescape(re.sub('<[^>]+>', ' ', paragraph)).split()
    assert len(words) <= 60, (len(words), words[:8])
print('Valid JSON-LD, matching five FAQs, five question sections, three distinct body links, four images, short paragraphs, disclaimer and no em dashes.')
