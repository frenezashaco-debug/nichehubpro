"""Conservative, repeatable first pass. Never labels an article medically verified.

No network, publishing clients, paragraph deletion, or invented citations.
--apply synchronizes manually selected titles and misleading internal anchors.
Both modes produce a 140-article review register with verbatim candidate claims.
"""
import argparse
from collections import Counter
from html import escape, unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'sleep-routine-tips', 'best-evening-habits-for-better-sleep',
            'daily-self-care-routine', 'how-to-build-habits-that-actually-stick'}
# Individually selected editorial replacements. URL slugs are not changed.
TITLES = {
 'benefits-of-walking-daily': '7 Benefits of Walking Daily to Consider',
 'best-daily-mobility-exercises': '5 Daily Mobility Exercises to Adapt to Your Needs',
 'best-free-productivity-apps-for-android-2026': '7 Free Android Productivity Apps to Compare in 2026',
 'best-habit-tracker-methods-that-work': '5 Habit Tracker Methods to Compare',
 'best-productivity-systems-explained': '7 Productivity Systems Explained: Choosing a Practical Fit',
 'daily-wellness-habits': '5 Daily Wellness Habits to Try at Your Own Pace',
 'deep-work-vs-multitasking': 'Deep Work vs Multitasking: 5 Differences to Consider',
 'fear-of-failure-anxiety': '5 Ways to Respond to Fear of Failure Anxiety',
 'foods-that-reduce-anxiety': '7 Food Choices to Consider Alongside Anxiety Care',
 'healthy-daily-habits': '7 Healthy Daily Habits to Build Gradually',
 'healthy-habits-to-start-this-week': '7 Healthy Habits to Start This Week at Your Own Pace',
 'healthy-lifestyle-tips': '7 Healthy Lifestyle Tips to Adapt to Your Day',
 'healthy-sleep-habits-that-improve-energy': '7 Sleep Habits to Support Daytime Energy',
 'how-to-break-negative-thinking': '5 Ways to Respond to Negative Thinking',
 'how-to-build-confidence': '5 Ways to Build Confidence Through Small Actions',
 'how-to-build-energy-that-lasts-all-day-without-crashing': '7 Ways to Plan for Steadier Energy During the Day',
 'how-to-change-your-mindset': '5 Ways to Reconsider Unhelpful Thinking Habits',
 'how-to-feel-calm-instantly': '5 Calming Techniques to Try When Stress Builds',
 'how-to-feel-happy-again': '7 Ways to Support Yourself When Happiness Feels Distant',
 'how-to-feel-in-control-of-your-mind': '3 Ways to Respond More Deliberately to Your Thoughts',
 'how-to-gamify-your-life-for-productivity': '7 Ways to Use Gamification for Everyday Goals',
 'how-to-improve-your-life': '7 Ways to Choose Practical Changes in Your Life',
 'how-to-increase-energy-naturally': '5 Everyday Habits to Support Your Energy',
 'how-to-reduce-anxiety-naturally': '7 Everyday Strategies to Support Anxiety Management',
 'how-to-relax-your-mind': '5 Ways to Make Space for Mental Rest',
 'how-to-sleep-better-naturally': '7 Sleep Habits to Try and When to Seek Help',
 'how-to-stay-calm-under-pressure': '5 Ways to Respond to Pressure More Deliberately',
 'how-to-stay-motivated': '7 Ways to Work With Changing Motivation',
 'how-to-stop-anxiety-attacks': '5 Ways to Respond to Intense Anxiety and Seek Support',
 'how-to-stop-panic-attacks': '5 Ways to Respond to Panic and Know When to Seek Help',
 'how-to-stop-procrastinating-immediately': '7 Practical Ways to Start a Task You Are Avoiding',
 'how-to-stop-procrastination': '7 Ways to Understand and Reduce Procrastination',
 'natural-energy-boosters': '7 Everyday Options for Supporting Your Energy',
 'the-emotional-root-of-chronic-procrastination': '7 Emotional Factors That Can Contribute to Procrastination',
 'why-you-always-feel-stressed': '5 Possible Contributors to Ongoing Stress',
 'why-you-feel-emotionally-numb': '7 Possible Contributors to Emotional Numbness',
}

CLAIMS = {
 'number_to_verify': r'\b\d+(?:\.\d+)?\s*(?:%|percent|times more|times less)',
 'evidence_to_verify': r'\b(?:studies|study|research)\b.{0,65}\b(?:shows?|found|proves?|according|published)\b',
 'institution_to_verify': r'\b(?:Harvard|Stanford|Mayo Clinic|Cleveland Clinic|APA|National Sleep Foundation|American Sleep Association|Porges)\b',
 'mechanism_to_verify': r'\b(?:dopamine|serotonin|vagus|cortisol|rewir\w*|amygdala|parasympathetic)\b',
 'outcome_to_verify': r'\b(?:cures?|guaranteed|eliminates?|permanently|forever|within \w+ (?:days|weeks)|in just \d+ days)\b',
 'anecdote_to_verify': r'\b(?:Sarah|Maria|John|Emma|James|Michael)\b',
}
RISKY_ANCHOR = re.compile(r'\b(?:transform\w*|instantly|forever|guarantee\w*|cure\w*|end insomnia|without pills|brain power|science-backed|no willpower|required|fix tight|unlock your|changes everything|finally make you feel alive)\b', re.I)
SKIP_CLASS = re.compile(r'nav|footer|sidebar|related|promo|author|breadcrumb|sources|tldr|toc|header', re.I)

class Node:
    def __init__(self, tag, attrs, start, inside, parent):
        self.tag, self.attrs, self.start, self.inside, self.parent = tag, dict(attrs), start, inside, parent
        self.end_inside = self.end = None

class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=False)
        self.text, self.nodes, self.stack = text, [], []
        self.offsets = [0]
        for match in re.finditer('\n', text):
            self.offsets.append(match.end())
        self.feed(text)

    def pos(self):
        line, col = self.getpos()
        return self.offsets[line - 1] + col

    def handle_starttag(self, tag, attrs):
        start = self.pos()
        n = Node(tag, attrs, start, start + len(self.get_starttag_text()), self.stack[-1] if self.stack else None)
        self.nodes.append(n)
        if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:
            self.stack.append(n)
        else:
            n.end_inside = n.end = n.inside

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i].tag == tag:
                n = self.stack[i]
                n.end_inside = self.pos()
                n.end = self.text.find('>', n.end_inside) + 1
                del self.stack[i:]
                return

    def inner(self, n):
        return self.text[n.inside:n.end_inside] if n.end_inside is not None else ''

def plain(text):
    return re.sub(r'\s+', ' ', unescape(re.sub(r'<[^>]+>', ' ', text))).strip()

def title(text):
    value = plain(re.search(r'<title>(.*?)</title>', text, re.S|re.I)[1])
    return re.sub(r'\s*(?:\||-)\s*NicheHubPro\s*$', '', value)

def article_slug(href):
    url = urlsplit(unescape(href))
    if url.netloc and url.netloc != 'nichehubpro.com':
        return None
    m = re.search(r'(?:^|/)articles/([^/]+)\.html$', url.path)
    return unquote(m[1]) if m else None

def transform(text, slug, titles):
    d = Document(text)
    patches, stats = [], Counter()
    def change(start, end, value, label):
        if text[start:end] != value:
            patches.append((start, end, value))
            stats[label] += 1
    for n in d.nodes:
        if n.end_inside is None:
            continue
        inner = d.inner(n)
        if n.tag in {'title', 'h1'}:
            value = titles[slug] + (' | NicheHubPro' if n.tag == 'title' else '')
            change(n.inside, n.end_inside, escape(value), 'heading')
        elif n.tag == 'meta' and n.attrs.get('property') in {'og:title', 'twitter:title'}:
            raw = text[n.start:n.end]
            value = re.sub(r'(content=")[^"]*', lambda m: m[1] + escape(titles[slug], quote=True), raw)
            change(n.start, n.end, value, 'social_title')
        elif n.tag == 'script' and n.attrs.get('type') == 'application/ld+json':
            data = json.loads(inner)
            changed = False
            def walk(obj):
                nonlocal changed
                if isinstance(obj, dict):
                    if obj.get('@type') in ('Article', 'BlogPosting') and obj.get('headline') != titles[slug]:
                        obj['headline'], changed = titles[slug], True
                    if obj.get('@type') == 'BreadcrumbList':
                        items = obj.get('itemListElement', [])
                        if items and items[-1].get('name') != titles[slug]:
                            items[-1]['name'], changed = titles[slug], True
                    for v in obj.values():
                        walk(v)
                elif isinstance(obj, list):
                    for v in obj:
                        walk(v)
            walk(data)
            if changed:
                change(n.inside, n.end_inside, '\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n ', 'schema')
        elif n.tag == 'span' and n.parent and 'breadcrumb' in n.parent.attrs.get('class', '') and 'breadcrumb-sep' not in n.attrs.get('class', '') and '<' not in inner:
            # Only the final current-page span, never a linked ancestor.
            change(n.inside, n.end_inside, escape(titles[slug]), 'breadcrumb')
        elif n.tag == 'a':
            dest = article_slug(n.attrs.get('href', ''))
            if dest in titles and '<' not in inner and RISKY_ANCHOR.search(plain(inner)):
                change(n.inside, n.end_inside, escape(titles[dest]), 'internal_anchor')
    last = len(text) + 1
    for start, end, value in sorted(patches, reverse=True):
        assert end <= last, 'Overlapping HTML edits'
        text = text[:start] + value + text[end:]
        last = start
    return text, dict(stats)

def audit(slug, text):
    d = Document(text)
    paragraphs, findings, sources = [], [], set()
    for n in d.nodes:
        if n.tag == 'a':
            href = n.attrs.get('href', '')
            u = urlsplit(href)
            if u.scheme == 'https' and u.netloc not in {'nichehubpro.com', 'play.google.com', 'www.pinterest.com'}:
                sources.add(href)
        if n.tag != 'p' or n.end_inside is None:
            continue
        parent, skip = n.parent, False
        while parent:
            if parent.tag in {'nav','footer','aside','script','style'} or SKIP_CLASS.search(parent.attrs.get('class','')):
                skip = True
            parent = parent.parent
        if skip:
            continue
        content = plain(d.inner(n))
        if len(content.split()) < 15:
            continue
        paragraphs.append(content)
        flags = [key for key, pat in CLAIMS.items() if re.search(pat, content, re.I)]
        if flags:
            findings.append({'line': text[:n.start].count('\n') + 1, 'flags': flags, 'text': content})
    return {'slug': slug, 'url': 'https://nichehubpro.com/articles/' + slug + '.html',
            'title': title(text), 'status': 'needs_individual_editorial_review',
            'body_paragraph_words': sum(len(p.split()) for p in paragraphs),
            'candidate_claims': findings, 'external_links_to_verify': sorted(sources),
            'faq_answers': text.count('class="faq-a"'),
            'has_disclaimer': 'does not replace professional medical advice' in text,
            'paragraphs': paragraphs}

def check(text, slug):
    d = Document(text)
    assert len([n for n in d.nodes if n.tag == 'h1']) == 1, slug
    for n in d.nodes:
        if n.tag == 'script' and n.attrs.get('type') == 'application/ld+json':
            json.loads(d.inner(n))
    for href in re.findall(r'href="([^"]+)"', text):
        dest = article_slug(href)
        if dest:
            assert (ROOT / 'articles' / (dest + '.html')).is_file(), (slug, href)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    files = {p.stem: p for p in sorted((ROOT / 'articles').glob('*.html'))}
    targets = sorted(set(files) - EXCLUDED)
    assert len(targets) == 140, len(targets)
    originals = {slug: p.read_text(encoding='utf-8') for slug, p in files.items()}
    titles = {slug: TITLES.get(slug, title(text)) for slug, text in originals.items()}
    report, changes = [], {}
    for slug in targets:
        before = originals[slug]
        after, stats = transform(before, slug, titles)
        check(after, slug)
        assert transform(after, slug, titles)[0] == after, ('not idempotent', slug)
        # Metadata/link-only pass: do not manufacture fresh publication dates.
        assert re.findall(r'"date(?:Published|Modified)"\s*:\s*"[^"]+"', before) == re.findall(r'"date(?:Published|Modified)"\s*:\s*"[^"]+"', after), slug
        if stats:
            changes[slug] = stats
            if args.apply:
                files[slug].write_text(after, encoding='utf-8')
        row = audit(slug, after if args.apply else before)
        row['applied_changes'] = stats if args.apply else {}
        report.append(row)
    # Synchronize catalog titles without regenerating articles or external posts.
    if args.apply:
        p = ROOT / 'articles.js'
        s = p.read_text(encoding='utf-8')
        m = re.search(r'const ARTICLES = (\[[\s\S]*?\]);', s)
        data = json.loads(m[1])
        for row in data:
            if row['slug'] in targets:
                row['title'] = titles[row['slug']]
        updated = s[:m.start(1)] + json.dumps(data, ensure_ascii=False, indent=2) + s[m.end(1):]
        if updated != s:
            p.write_text(updated, encoding='utf-8')
        p = ROOT / 'api/articles.json'
        s = p.read_text(encoding='utf-8')
        data = json.loads(s)
        for row in data:
            if row['id'] in targets:
                row['title'] = titles[row['id']]
        updated = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
        if updated != s:
            p.write_text(updated, encoding='utf-8')
    repeated = Counter(p for row in report for p in row.pop('paragraphs'))
    for row in report:
        row['duplicate_body_paragraphs'] = sum(1 for p in audit(row['slug'], originals[row['slug']])['paragraphs'] if repeated[p] > 1)
    report.sort(key=lambda row: (-len(row['candidate_claims']), row['slug']))
    out = ROOT / 'reports' / 'batch-140'
    out.mkdir(parents=True, exist_ok=True)
    payload = {'scope': 140, 'mode': 'applied' if args.apply else 'audit',
               'modified_articles': len(changes) if args.apply else 0,
               'articles_with_candidate_claims': sum(bool(r['candidate_claims']) for r in report),
               'candidate_claim_count': sum(len(r['candidate_claims']) for r in report),
               'warning': 'Candidates are not proven errors. Zero flags is not editorial or medical approval. Originality and citation support require individual review.',
               'articles': report}
    (out / 'register.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    lines = ['# Batch de 140 articles', '', payload['warning'], '',
             f"Mode: {payload['mode']}. Articles modifies: {payload['modified_articles']}.",
             f"Articles avec candidats a verifier: {payload['articles_with_candidate_claims']}. Passages: {payload['candidate_claim_count']}.", '',
             '| Article | Passages a verifier | Mots des paragraphes | Etat |', '|---|---:|---:|---|']
    for row in report:
        lines.append(f"| [{row['title'].replace('|', '/')} ]({row['url']}) | {len(row['candidate_claims'])} | {row['body_paragraph_words']} | Revue individuelle requise |")
    (out / 'register.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in payload.items() if k != 'articles'}, indent=2))
    print('First 10:', ', '.join(r['slug'] for r in report[:10]))

if __name__ == '__main__':
    main()
