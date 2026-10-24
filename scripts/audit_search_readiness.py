"""Read-only public sitemap audit. Writes local evidence, never edits the site."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import ssl
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

BASE = 'https://nichehubpro.com'
CONTEXT = ssl.create_default_context()


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonicals = []
        self.noindex = False
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'link' and 'canonical' in attrs.get('rel', '').split():
            self.canonicals.append(attrs.get('href'))
        if tag == 'meta' and attrs.get('name', '').lower() in ('robots', 'googlebot'):
            self.noindex |= 'noindex' in attrs.get('content', '').lower()


def fetch(url):
    with urlopen(Request(url, headers={'User-Agent': 'NicheHubPro-Public-Audit/1.0'}),
                 context=CONTEXT, timeout=25) as response:
        return response.status, response.url, dict(response.headers), response.read()


def inspect(url):
    try:
        status, final, headers, body = fetch(url)
        tags = Tags()
        tags.feed(body.decode('utf-8', errors='replace'))
        issues = []
        if final != url:
            issues.append('sitemap URL redirects')
        if tags.canonicals != [url]:
            issues.append('canonical missing, multiple or different')
        if tags.noindex or 'noindex' in headers.get('X-Robots-Tag', '').lower():
            issues.append('noindex')
        return {'url': url, 'status': status, 'final': final,
                'canonicals': tags.canonicals, 'issues': issues}
    except Exception as error:
        return {'url': url, 'issues': [type(error).__name__ + ': ' + str(error)]}


def main():
    _, _, _, sitemap = fetch(BASE + '/sitemap.xml')
    urls = [node.text for node in ET.fromstring(sitemap).iter()
            if node.tag.endswith('}loc') or node.tag == 'loc']
    if not urls or any(not url.startswith(BASE + '/') for url in urls):
        raise RuntimeError('Unexpected sitemap URL inventory')
    with ThreadPoolExecutor(max_workers=8) as executor:
        rows = list(executor.map(inspect, urls))
    report = {'checked_at': datetime.now(timezone.utc).isoformat(),
              'sitemap_urls': len(urls), 'duplicate_urls': len(urls) - len(set(urls)),
              'issue_count': sum(bool(row['issues']) for row in rows), 'pages': rows}
    target = Path(__file__).resolve().parents[1] / 'reports' / 'search-readiness-latest.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key != 'pages'}, indent=2))
    print(json.dumps([row for row in rows if row['issues']], indent=2))


if __name__ == '__main__':
    main()
