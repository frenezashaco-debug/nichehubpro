"""Read-only checks for the week-one distribution bundle. No API calls."""
import json
import re
import struct
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, parse_qs, unquote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
BUNDLE = Path(__file__).resolve().parent

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.ids = []
        self.canonicals = []
        self.faq = 0
        self.h1 = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "a":
            self.links.append(a.get("href", ""))
        if tag == "link" and a.get("rel") == "canonical":
            self.canonicals.append(a.get("href"))
        if "faq-item" in a.get("class", "").split():
            self.faq += 1
        if tag == "h1":
            self.h1 += 1

pins = json.loads((BUNDLE / "pinterest.json").read_text(encoding="utf-8"))
assert len(pins) == 6
assert len({p["id"] for p in pins}) == 6
slugs = set()
for p in pins:
    assert len(p["title"]) <= 100 and len(p["description"]) <= 500
    assert p["status"] == "draft_not_scheduled" and p["published_url"] is None
    assert p["planned_time"] is None
    url = urlsplit(p["destination_url"])
    assert url.hostname == "nichehubpro.com"
    assert parse_qs(url.query)["utm_source"] == ["pinterest"]
    assert p["canonical_url"] == "https://nichehubpro.com" + url.path
    image = ROOT / p["image"]
    data = image.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    width, height = struct.unpack(">II", data[16:24])
    assert width * 3 == height * 2
    slugs.add(Path(url.path).stem)
    print(p["id"], len(p["title"]), len(p["description"]), width, height)

ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
site = ET.parse(ROOT / "sitemap.xml")
sitemap_urls = {u.find("s:loc", ns).text: u for u in site.findall("s:url", ns)}
for slug in sorted(slugs):
    path = ROOT / "articles" / (slug + ".html")
    html = path.read_text(encoding="utf-8")
    page = Page()
    page.feed(html)
    expected = "https://nichehubpro.com/articles/" + slug + ".html"
    assert page.canonicals == [expected], (slug, page.canonicals)
    assert page.h1 == 1 and page.faq == 5, (slug, page.h1, page.faq)
    assert len(page.ids) == len(set(page.ids)), (slug, "duplicate IDs")
    assert expected in sitemap_urls
    assert sitemap_urls[expected].find("s:lastmod", ns).text == "2026-09-19"
    assert "does not replace professional medical advice" in html
    assert "https://www.ni" in html or "https://www.nhlbi" in html
    assert "\u2014" not in html
    for source in re.findall(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S):
        obj = json.loads(source)
        if obj.get("@type") in ("Article", "BlogPosting"):
            assert obj["dateModified"] == "2026-09-19"
    for link in page.links:
        url = urlsplit(link)
        if url.scheme or url.netloc or not url.path:
            continue
        target = ROOT / unquote(url.path.lstrip("/")) if url.path.startswith("/") else path.parent / unquote(url.path)
        if target.suffix == ".html":
            assert target.is_file(), (slug, link)
    print(slug, "canonical, FAQ, schema, sitemap and HTML links OK")

for draft in sorted(BUNDLE.glob("medium-*.md")):
    text = draft.read_text(encoding="utf-8")
    assert "\u2014" not in text and not re.search(r"\bdelve\b", text, re.I)
    assert "utm_source=medium" in text and "https://www.n" in text
    assert len(text.split()) >= 400
    print(draft.name, len(text.split()), "words")
assert "PUBLISHING_PAUSED = True" in (ROOT / "batch_24weeks.py").read_text(encoding="utf-8")
workflow = (ROOT / ".github/workflows/daily_publish.yml").read_text(encoding="utf-8")
assert not re.search(r"^\s*schedule:", workflow, re.M)
print("PASS: local structural checks only, not clinical review or platform scheduling.")
