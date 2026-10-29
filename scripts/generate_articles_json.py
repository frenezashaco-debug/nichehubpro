import os, json, re, argparse
from html import unescape
from datetime import datetime

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

def get_category(slug, title=''):
    s = (slug + ' ' + title).lower()
    if any(k in s for k in ['productivity', 'focus', 'phone', 'routine',
                              'review', 'work', 'distraction', 'habit',
                              'journal', 'morning', 'weekly', 'overthink',
                              'procrastin']):
        return 'productivity'
    if any(k in s for k in ['food', 'eating', 'diet', 'nutrition', 'walking',
                              'exercise', 'fitness', 'strength', 'training',
                              'lemon', 'water', 'magnesium', 'probiotic',
                              'anti-aging', 'aging', 'lifestyle', 'sleep',
                              'healthy', 'anti', 'vitamin', 'weight', 'calm',
                              'relax', 'breathe', 'breath']):
        return 'healthy_lifestyle'
    return 'mental_wellness'

def parse_article(file_path, slug):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    title = description = date = None

    # Extract from JSON-LD (most reliable)
    ld_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', content, re.S)
    if ld_match:
        try:
            ld = json.loads(ld_match.group(1))
            title = ld.get('headline') or ld.get('name')
            description = ld.get('description')
            date = (ld.get('datePublished') or ld.get('dateModified') or '')[:10]
        except Exception:
            pass

    # Fallback to meta tags
    if not title:
        if HAS_BS4:
            soup = BeautifulSoup(content, 'html.parser')
            t = soup.find('title')
            if t:
                title = t.get_text().split('|')[0].strip()
        else:
            m = re.search(r'<title>(.*?)</title>', content, re.I | re.S)
            if m:
                title = re.sub(r'<[^>]+>', '', m.group(1)).split('|')[0].strip()

    if not description:
        m = re.search(r'name=["\']description["\'][^>]*content=["\']([^"\']+)', content, re.I)
        if m:
            description = m.group(1).strip()

    if not title or not date:
        return None

    if not description or len(description) < 20:
        description = 'Read about ' + title.lower() + ' on NicheHubPro.'

    # The published article's explicit taxonomy wins over keyword guesses.
    tag = re.search(r'<span\b[^>]*class=["\']article-tag["\'][^>]*>(.*?)</span>', content, re.I | re.S)
    categories = {'mental wellness': 'mental_wellness', 'productivity': 'productivity', 'healthy lifestyle': 'healthy_lifestyle'}
    label = unescape(re.sub(r'<[^>]+>', '', tag.group(1))).strip().lower() if tag else ''
    category = categories.get(label) or get_category(slug, title)

    return {
        'id': slug,
        'title': title,
        'shortText': description[:160],
        'category': category,
        'url': 'https://nichehubpro.com/articles/' + slug + '.html',
        'date': date
    }

def main():
    parser = argparse.ArgumentParser(description='Generate or verify the public article catalogue.')
    parser.add_argument('--check', action='store_true', help='Fail if the catalogue differs from the published HTML files.')
    args = parser.parse_args()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    articles_dir = os.path.join(root, 'articles')
    articles = []

    for filename in sorted(os.listdir(articles_dir)):
        if not filename.endswith('.html'):
            continue
        slug = filename[:-5]  # remove .html
        file_path = os.path.join(articles_dir, filename)
        article = parse_article(file_path, slug)
        if article:
            articles.append(article)
        else:
            raise ValueError('Cannot catalogue published article: ' + filename)

    articles.sort(key=lambda x: x['date'], reverse=True)

    out = os.path.join(root, 'api', 'articles.json')
    if args.check:
        with open(out, 'r', encoding='utf-8') as f:
            existing = json.load(f)
        if existing != articles:
            expected_ids = {row['id'] for row in articles}
            actual_ids = {row['id'] for row in existing}
            raise SystemExit('Article catalogue is out of sync. Missing: ' +
                             ', '.join(sorted(expected_ids - actual_ids)) +
                             '; stale: ' + ', '.join(sorted(actual_ids - expected_ids)) +
                             '. Regenerate it before publication.')
        print('PASS - all ' + str(len(articles)) + ' published articles match api/articles.json')
        return
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)

    print('Done - ' + str(len(articles)) + ' articles written to api/articles.json')

if __name__ == '__main__':
    main()
