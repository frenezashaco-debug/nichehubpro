"""Repair missing list/inline closures at article section boundaries.

Insert only explicit closing tags; preserve every text node, URL and asset.
"""
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class Repair(HTMLParser):
    def __init__(self, raw):
        super().__init__(convert_charrefs=False)
        self.offsets = [0]
        for line in raw.splitlines(keepends=True):
            self.offsets.append(self.offsets[-1] + len(line))
        self.insertions = defaultdict(str)
        self.lists = []
        self.items = set()
        self.inline = []
        self.feed(raw)

    def insert(self, text):
        line, column = self.getpos()
        self.insertions[self.offsets[line - 1] + column] += text

    def close_inline(self):
        while self.inline:
            self.insert('</' + self.inline.pop() + '>')

    def close_lists(self):
        while self.lists:
            depth = len(self.lists)
            if depth in self.items:
                self.insert('</li>')
                self.items.remove(depth)
            self.insert('</' + self.lists.pop() + '>')

    def handle_starttag(self, tag, attrs):
        if tag in {'p', 'h1', 'h2', 'h3', 'h4', 'ul', 'ol', 'li', 'div'}:
            self.close_inline()
        if tag == 'h2':
            self.close_lists()
        if tag in {'ul', 'ol'}:
            self.lists.append(tag)
        if tag == 'li':
            depth = len(self.lists)
            if depth in self.items:
                self.insert('</li>')
            self.items.add(depth)
        if tag in {'em', 'strong'}:
            self.inline.append(tag)

    def handle_endtag(self, tag):
        if tag in {'p', 'li', 'h1', 'h2', 'h3', 'h4', 'div'}:
            self.close_inline()
        if tag in {'em', 'strong'} and tag in self.inline:
            while self.inline and self.inline[-1] != tag:
                self.insert('</' + self.inline.pop() + '>')
            self.inline.pop()
        if tag == 'li':
            self.items.discard(len(self.lists))
        if tag in {'ul', 'ol'} and self.lists:
            depth = len(self.lists)
            if depth in self.items:
                self.insert('</li>')
                self.items.remove(depth)
            self.lists.pop()
        if tag == 'article':
            self.close_inline()
            self.close_lists()

plans = []
for file in sorted((ROOT / 'articles').glob('*.html')):
    raw = file.read_text(encoding='utf-8')
    repair = Repair(raw)
    if repair.insertions:
        for offset, text in sorted(repair.insertions.items(), reverse=True):
            raw = raw[:offset] + text + raw[offset:]
        plans.append((file, raw, len(repair.insertions)))
for file, raw, count in plans:
    file.write_text(raw, encoding='utf-8', newline='')
print(f'Repaired {sum(p[2] for p in plans)} list/inline boundaries across {len(plans)} articles.')
