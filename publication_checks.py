"""Offline publication blockers, not factual verification or medical review."""
import html
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse


class Links(HTMLParser):
    def __init__(self, markup):
        super().__init__(convert_charrefs=True)
        self.hrefs = []
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.hrefs.extend(value for key, value in attrs if key == 'href' and value)


def publication_blockers(data, root):
    root = Path(root).resolve()
    errors = []
    # Inspect rendered body content, not just the model's link inventory.
    sections = data.get('sections') or []
    body_fields = [str(data.get(k, '')) for k in ('intro', 'tldr', 'real_example', 'conclusion')]
    body_fields += [str(s.get('content', '')) for s in sections]
    body_fields += [str(item.get('answer', '')) for item in data.get('faq', [])]
    if len(sections) == 5:
        body_links = []
        for field in body_fields:
            for href in Links(field).hrefs:
                parsed = urlparse(urljoin('https://nichehubpro.com/articles/draft.html', href))
                if parsed.hostname in ('nichehubpro.com', 'www.nichehubpro.com') and parsed.path.startswith('/articles/'):
                    if not href.startswith('#'):
                        body_links.append(href)
        if not 3 <= len(body_links) <= 5:
            errors.append(f'rendered body must contain 3-5 article links, got {len(body_links)}')
        for field in body_fields:
            paragraphs = re.findall(r'<p\b[^>]*>(.*?)</p>', field, re.S | re.I)
            if not paragraphs:
                paragraphs = [part for part in field.splitlines() if part.strip()]
            for paragraph in paragraphs:
                visible = html.unescape(re.sub(r'<[^>]+>', ' ', paragraph))
                if len(visible.split()) > 60:
                    errors.append('body paragraph exceeds 60 words; split into short paragraphs')
        promise = re.search(r'\b(\d+)\s+(?:practical\s+)?(checks|steps|reasons|tips|ways|lessons)\b', str(data.get('title', '')), re.I)
        if promise:
            count = int(promise[1])
            noun = promise[2].lower().rstrip('s')
            body = '\n'.join(body_fields)
            labels = {int(n) for n in re.findall(r'\b' + noun + r'\s+(\d+)\s*[:.)]', html.unescape(re.sub(r'<[^>]+>', ' ', body)), re.I)}
            lists = re.findall(r'<ol\b[^>]*>(.*?)</ol>', body, re.S | re.I)
            matches_list = any(len(re.findall(r'<li\b', block, re.I)) == count for block in lists)
            if labels != set(range(1, count + 1)) and not matches_list:
                errors.append('numbered title needs matching explicit numbered labels or an ordered list in the body')
    fields = [data.get(k, '') for k in ('title', 'meta_description', 'intro', 'tldr', 'real_example', 'conclusion')]
    for section in data.get('sections', []):
        fields.extend([section.get('h2', ''), section.get('content', '')])
    for faq in data.get('faq', []):
        fields.extend([faq.get('question', ''), faq.get('answer', '')])
    for group in ('internal_links', 'related'):
        for link in data.get(group, []):
            slug = str(link.get('slug', ''))
            if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
                errors.append(f'{group}: invalid article slug')
            elif not (root / 'articles' / (slug + '.html')).is_file():
                errors.append(f'{group}: missing article {slug}')

    references = {str(r.get('url', '')).strip() for r in data.get('references', [])}
    for field in fields:
        markup = str(field)
        for href in Links(markup).hrefs:
            parsed = urlparse(urljoin('https://nichehubpro.com/articles/draft.html', href))
            if parsed.hostname not in ('nichehubpro.com', 'www.nichehubpro.com'):
                continue
            target_path = unquote(parsed.path)
            target = (root / target_path.lstrip('/')).resolve()
            if root not in target.parents and target != root:
                errors.append('internal link escapes site root')
                continue
            if target.is_dir():
                target = target / 'index.html'
            # Fragment existence is outside this local-file check.
            if href.startswith('#'):
                continue
            if not target.is_file():
                errors.append(f'internal link has no local destination: {parsed.path}')
        text = html.unescape(re.sub(r'<[^>]+>', ' ', markup))
        if '\u2014' in text:
            errors.append('em dash is prohibited, including encoded HTML entities')
        if re.search(r'Images in this article are AI-generated illustrations', text, re.I):
            errors.append('unwanted image boilerplate in article copy')
        # Narrow confirmed regressions, not a comprehensive semantic classifier.
        patterns = (
            r'\byour (?:heart|body) is safe\b',
            r'\bno sunglasses\b',
            r'\blet the light hit your eyes directly\b',
            r'\bdunk your face\b',
            r'\bdopamine.{0,35}resets? every 24 hours\b',
            r'\b(?:remove the unsupported|insert citation|source needed)\b',
            r'\brequire editorial verification before publication\b',
        )
        for pattern in patterns:
            if re.search(pattern, text, re.I):
                errors.append('prohibited safety claim or editing placeholder: ' + pattern)
        # A nearby citation is a minimum traceability requirement, not evidence validation.
        for block in re.split(r'</(?:p|li|div)>|\n', markup):
            visible = html.unescape(re.sub(r'<[^>]+>', ' ', block))
            if re.search(r'\b(?:research.{0,90}?(?:shows?|proves?|found)|stud(?:y|ies).{0,90}?(?:shows?|proves?|found)|scientifically proven)\b', visible, re.I):
                if not any(url in references and url.startswith('https://') for url in Links(block).hrefs):
                    errors.append('research attribution needs an inline listed source and verification of its scope')
            if re.search(r'\b(?:boosts?|raises?|lowers?|increases?|reduces?|burns?|resets?|restarts?)\b.{0,45}\b(?:cortisol|dopamine|serotonin)\b|\b(?:rewires? (?:your |the )?brain|vagus nerve responds instantly|dopamine system is offline)\b', visible, re.I):
                if not any(url in references and url.startswith('https://') for url in Links(block).hrefs):
                    errors.append('biological mechanism needs an inline listed source and verification of its scope')
            if re.search(r'\b\d+(?:\.\d+)?\s*(?:%|percent\b)', visible, re.I):
                if not any(url in references and url.startswith('https://') for url in Links(block).hrefs):
                    errors.append('percentage needs an inline link to a listed source; remove it if unverifiable')
    example = html.unescape(re.sub(r'<[^>]+>', ' ', str(data.get('real_example', ''))))
    if re.search(r'\b(?:scored|improved|recovered|lost|gained)\b.{0,50}\b\d+\b', example, re.I):
        errors.append('illustrative example must not invent measured outcomes')
    return list(dict.fromkeys(errors))
