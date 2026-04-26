import os, json, re
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

    return {
        'id': slug,
        'title': title,
        'shortText': description[:160],
        'category': get_category(slug, title),
        'url': 'https://nichehubpro.com/articles/' + slug + '.html',
        'date': date
    }

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    articles_dir = os.path.join(root, 'articles')
    articles = []

    for filename in os.listdir(articles_dir):
        if not filename.endswith('.html'):
            continue
        slug = filename[:-5]  # remove .html
        file_path = os.path.join(articles_dir, filename)
        article = parse_article(file_path, slug)
        if article:
            articles.append(article)

    articles.sort(key=lambda x: x['date'], reverse=True)

    out = os.path.join(root, 'api', 'articles.json')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)

    print('Done - ' + str(len(articles)) + ' articles written to api/articles.json')

if __name__ == '__main__':
    main()