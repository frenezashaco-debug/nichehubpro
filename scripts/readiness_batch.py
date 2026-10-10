"""Read-only site audit. Findings are review signals, not AdSense decisions.

Usage: python scripts/readiness_batch.py [--live] [--pagespeed]
Reports are written under reports/readiness. No publishing or webhooks run.
"""
import argparse
import concurrent.futures
import json
import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://nichehubpro.com'


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.links, self.images, self.headings, self.canonical = [], [], [], []
        self.noindex = False
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'a' and a.get('href'):
            self.links.append(a['href'])
        if tag == 'img':
            self.images.append(a)
        if tag in ('h1', 'h2'):
            self.headings.append(tag)
        if tag == 'link' and 'canonical' in a.get('rel', '').split():
            self.canonical.append(a.get('href'))
        if tag == 'meta' and a.get('name', '').lower() in ('robots', 'googlebot'):
            self.noindex |= 'noindex' in a.get('content', '').lower()


def local(url):
    path = urllib.parse.unquote(urllib.parse.urlsplit(url).path).lstrip('/')
    candidate = (ROOT / path).resolve()
    if not candidate.is_relative_to(ROOT):
        return None
    if candidate.is_dir():
        candidate /= 'index.html'
    return candidate


def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'NicheHubProReadiness/1.0'})
    try:
        with urllib.request.urlopen(request, timeout=35) as response:
            body = response.read()
            return {'url': url, 'status': response.status, 'final_url': response.url,
                    'type': response.headers.get('Content-Type', ''), 'body': body.decode('utf-8', errors='replace')}
    except Exception as error:
        return {'url': url, 'error': type(error).__name__, 'status': getattr(error, 'code', None)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--pagespeed', action='store_true')
    args = parser.parse_args()
    urls = [n.text for n in ET.parse(ROOT / 'sitemap.xml').iter() if n.tag.endswith('}loc')]
    findings, articles = [], []
    def flag(url, code, detail):
        findings.append({'url': url, 'code': code, 'detail': detail})
    for url, count in Counter(urls).items():
        if count > 1:
            flag(url, 'duplicate_sitemap', str(count))
        file = local(url)
        if not file or not file.is_file():
            flag(url, 'missing_page', 'Sitemap URL has no local file')
            continue
        source = file.read_text(encoding='utf-8')
        page = Page(source)
        if page.canonical != [url]:
            flag(url, 'canonical', str(page.canonical))
        if page.noindex:
            flag(url, 'noindex_in_sitemap', 'Review intended indexability')
        if page.headings.count('h1') != 1:
            flag(url, 'h1_count', str(page.headings.count('h1')))
        for target in set(page.links + [im.get('src', '') for im in page.images]):
            resolved = urllib.parse.urljoin(url, target)
            if urllib.parse.urlsplit(resolved).netloc != 'nichehubpro.com':
                continue
            dest = local(resolved)
            if not dest or not dest.is_file():
                flag(url, 'missing_local_target', target)
        if '/articles/' in url:
            external = [link for link in page.links if link.startswith('https://') and 'nichehubpro.com' not in urllib.parse.urlsplit(link).netloc]
            articles.append({'url': url, 'images': len(page.images), 'external_links': len(external)})
            if len(page.images) < 4:
                flag(url, 'image_count_review', str(len(page.images)))
            if not re.search(r'faq|frequently asked', source, re.I):
                flag(url, 'faq_review', 'No FAQ marker detected')
            if not re.search(r'sources|references', source, re.I):
                flag(url, 'sources_review', 'No sources marker detected')
            if 'require editorial verification before publication' in source:
                flag(url, 'editorial_review_pending', 'Draft notice remains')
    report = {'scope': 'Local sitemap pages; redirects and factual accuracy need separate review',
              'sitemap_urls': len(urls), 'articles': articles, 'findings': findings,
              'counts': dict(Counter(item['code'] for item in findings)),
              'manual_checks': ['AdSense certified CMP and consent choices', 'Make history and deduplication',
                                'Medical source-to-claim review', 'Search Console traffic export']}
    samples = [SITE + '/', SITE + '/healthy-lifestyle/'] + [a['url'] for a in articles[:3]]
    if args.live:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            report['live'] = list(pool.map(fetch, samples + [SITE + '/sitemap.xml', SITE + '/ads.txt']))
        for result in report['live']:
            result.pop('body', None)
        runs = fetch('https://api.github.com/repos/frenezashaco-debug/nichehubpro/actions/workflows/daily_publish.yml/runs?per_page=3')
        if runs.get('status') == 200:
            report['workflow_runs'] = [{k: r.get(k) for k in ('id', 'conclusion', 'created_at', 'html_url')} for r in json.loads(runs['body']).get('workflow_runs', [])]
        else:
            report['workflow_check'] = runs
    if args.pagespeed:
        report['pagespeed'] = []
        for url in samples[:2]:
            result = fetch('https://www.googleapis.com/pagespeedonline/v5/runPagespeed?' + urllib.parse.urlencode({'url': url, 'strategy': 'mobile', 'category': 'performance'}))
            body = result.pop('body', '')
            if result.get('status') == 200:
                data = json.loads(body)
                result['performance'] = data.get('lighthouseResult', {}).get('categories', {}).get('performance', {}).get('score')
            report['pagespeed'].append(result)
    output = ROOT / 'reports' / 'readiness'
    output.mkdir(parents=True, exist_ok=True)
    (output / 'latest.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    summary = ['# Website readiness batch', '', f'Sitemap URLs: {len(urls)}', f'Articles checked: {len(articles)}', '',
               'These are automated review signals, not a quality score or approval guarantee.', '']
    summary += [f'- {code}: {count}' for code, count in report['counts'].items()]
    summary += ['', 'See latest.json for page-level findings and optional live checks.', '', '## Requires verification', '']
    summary += ['- ' + item for item in report['manual_checks']]
    (output / 'latest.md').write_text('\n'.join(summary) + '\n', encoding='utf-8')
    print(json.dumps({'sitemap_urls': len(urls), 'article_count': len(articles), 'counts': report['counts'], 'report': str(output)}, indent=2))


if __name__ == '__main__':
    main()
