"""Inventory every article; flags are review leads, never scientific certification."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def audit():
    rows = []
    reference_claims = set()
    for path in sorted((ROOT / 'articles').glob('*.html')):
        raw = path.read_text(encoding='utf-8')
        for claim, url in re.findall(r'<em>([^<]*)</em>\s*-\s*<a[^>]*href="([^"]+)"', raw, re.S):
            reference_claims.add((html.unescape(re.sub('<[^>]+>', ' ', claim)).strip(), url))
        copy = re.sub(r'<(script|style)\b[^>]*>.*?</\1>', '', raw, flags=re.S | re.I)
        findings = []
        for match in re.finditer(r'<(p|li|div)\b[^>]*>([^<>]*(?:<(?!/?(?:p|li|div)\b)[^>]*>[^<>]*)*)</\1>', copy, re.S | re.I):
            block = match.group(0)
            text = html.unescape(re.sub('<[^>]+>', ' ', block))
            text = re.sub(r'\s+', ' ', text).strip()
            labels = []
            if re.search(r'research (?:shows|proves|found)|studies (?:show|prove)|scientifically proven', text, re.I):
                labels.append('evidence attribution needs source verification')
            if re.search(r'\d+(?:\.\d+)?\s*(?:%|percent\b)', text, re.I):
                labels.append('quantified statement needs context and verification')
            if re.search(r'(?:cortisol|dopamine|vagus|serotonin|rewir|nervous system)', text, re.I):
                labels.append('mechanism claim needs review')
            if labels:
                findings.append({'flags': labels, 'text': text, 'inline_urls': re.findall(r'href=[\"\x27](https?://[^\"\x27]+)', block)})
        decoded = html.unescape(raw)
        rows.append({'file': path.relative_to(ROOT).as_posix(),
                     'em_dash_count': decoded.count('\u2014'),
                     'ai_caption_count': len(re.findall(r'Images in this article are AI-generated illustrations', decoded, re.I)),
                     'images': re.findall(r'<img\b[^>]*src=[\"\x27]([^\"\x27]+)', raw, re.I),
                     'responsive_images': re.findall(r'<source\b[^>]*srcset=[\"\x27]([^\"\x27]+)', raw, re.I),
                     'pixel_watermarks': 'NOT VISUALLY VERIFIED',
                     'findings': findings})
    output = ROOT / 'reports' / 'all-article-copy-audit.json'
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding='utf-8')
    (ROOT / 'reports' / 'reference-claim-inventory.json').write_text(json.dumps(sorted(reference_claims), indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({'articles': len(rows), 'em_dashes': sum(r['em_dash_count'] for r in rows),
                      'ai_captions': sum(r['ai_caption_count'] for r in rows),
                      'articles_needing_claim_review': sum(bool(r['findings']) for r in rows),
                      'flagged_blocks': sum(len(r['findings']) for r in rows)}))

if __name__ == '__main__':
    audit()
