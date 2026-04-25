import os, json, re
from datetime import datetime

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

SKIP = {'api', 'articles', 'about', 'all-articles', 'assets', 'css', 'js',
        'images', 'scripts', '.github', '_site'}

def get_category(slug):
    s = slug.lower()
    if any(k in s for k in ['productivity', 'focus', 'phone', 'routine',
                              'review', 'work', 'distraction', 'habit',
                              'journal', 'morning', 'weekly']):
        return 'productivity'
    if any(k in s for k in ['food', 'eating', 'diet', 'nutrition', 'walking',
                              'exercise', 'fitness', 'strength', 'training',
                              'lemon', 'water', 'magnesium', 'probiotic',
                              'anti-aging', 'aging', 'lifestyle', 'sleep',
                              'healthy', 'anti']):
        return 'healthy_lifestyle'
    return 'mental_wellness'

def parse_article(folder_path, slug):
    index_file = os.path.join(folder_path, 'index.html')
    if not os.path.exists(index_file):
        return None

    with open(index_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    title = description = date = None

    if HAS_BS4:
        soup = BeautifulSoup(content, 'html.parser')
        h1 = soup.find('h1')
        if h1:
            title = h1.get_text().strip()
        if not title:
            t = soup.find('title')
            if t:
                title = t.get_text().split('|')[0].split(chr(8211))[0].strip()
        meta_d = soup.find('meta', attrs={'name': 'description'})
        if meta_d:
            description = meta_d.get('content', '').strip()
        meta_date = soup.find('meta', attrs={'property': 'article:published_time'})
        if meta_date:
            date = meta_date.get('content', '')[:10]
        if not date:
            time_tag = soup.find('time')
            if time_tag:
                date = (time_tag.get('datetime') or time_tag.get_text())[:10]
    else:
        m = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.I | re.S)
        if m:
            title = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        m = re.search(r'name=["\']description["\'][^>]*content=["\']([^"\']+)', content, re.I)
        if m:
            description = m.group(1).strip()
        m = re.search(r'article:published_time[^>]*content=["\'](\d{4}-\d{2}-\d{2})', content, re.I)
        if m:
            date = m.group(1)

    if not title:
        title = slug.replace('-', ' ').title()
    if not description:
        description = 'Read about ' + title.lower() + ' on NicheHubPro.'
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')

    return {
        'id': slug,
        'title': title,
        'shortText': description[:160],
        'category': get_category(slug),
        'url': 'https://nichehubpro.com/' + slug + '/',
        'date': date
    }

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    articles = []

    for item in sorted(os.listdir(root)):
        if item.startswith('.') or item in SKIP:
            continue
        folder = os.path.join(root, item)
        if not os.path.isdir(folder):
            continue
        article = parse_article(folder, item)
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