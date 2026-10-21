"""Lossless paragraph formatting; never rewrite claims or remove checks."""
import copy
import html
import re


def words(value):
    return len(html.unescape(re.sub(r'<[^>]+>', ' ', value)).split())


def split_paragraph(value, separator):
    if words(value) <= 60:
        return value
    # Only split outside inline HTML, retaining links and emphasis intact.
    stack = []
    boundaries = []
    for token in re.finditer(r'<[^>]+>|[^<]+', value):
        part = token.group()
        if part.startswith('<'):
            tag = re.match(r'</?([a-zA-Z0-9]+)', part)
            if tag:
                name = tag[1].lower()
                if part.startswith('</'):
                    if stack and stack[-1] == name:
                        stack.pop()
                elif name not in ('br', 'img', 'hr', 'wbr') and not part.endswith('/>'):
                    stack.append(name)
        elif not stack:
            boundaries.extend(token.start() + m.end() for m in re.finditer(r'[.!?]["\u201d\u2019]?\s+', part))
    start = 0
    chunks = []
    while words(value[start:]) > 60:
        candidates = [b for b in boundaries if b > start and words(value[start:b]) <= 60]
        if not candidates:
            return value  # A long sentence/inline span needs rewriting, not truncation.
        end = max(candidates)
        chunks.append(value[start:end].strip())
        start = end
    chunks.append(value[start:].strip())
    return separator.join(chunks)


def repair_paragraphs(data):
    result = copy.deepcopy(data)
    # Intro, example and conclusion have exact paragraph counts: leave them intact.
    for section in result.get('sections', []):
        content = section.get('content', '')
        # Move generated numbering into body copy; H2 remains a question.
        heading = section.get('h2', '')
        numbered = re.match(r'^\s*(Check\s+[1-5])\s*:\s*(.+)$', heading, re.I | re.S)
        if numbered:
            section['h2'] = numbered[2]
            if not re.search(r'\b' + re.escape(numbered[1]) + r'\s*:', content, re.I):
                content = '<p><strong>' + numbered[1] + ': ' + numbered[2] + '</strong></p>' + content
        section['content'] = re.sub(
            r'(<p\b[^>]*>)(.*?)(</p>)',
            lambda m: m[1] + split_paragraph(m[2], m[3] + m[1]) + m[3],
            content, flags=re.I | re.S)
    for faq in result.get('faq', []):
        answer = faq.get('answer', '')
        if not re.search(r'<(?:p|ul|ol|li|div)\b', answer, re.I):
            faq['answer'] = split_paragraph(answer, '\n')
    return result
