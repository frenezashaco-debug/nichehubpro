"""Rebuild the static latest-article cards on the homepage from articles.js.

The homepage is intentionally crawlable without JavaScript, so its six newest
cards must be refreshed whenever the catalogue changes.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / "articles.js"
HOMEPAGE = ROOT / "index.html"
START = "<!-- LATEST_CARDS_START -->"
END = "<!-- LATEST_CARDS_END -->"


def load_articles() -> list[dict]:
    source = CATALOGUE.read_text(encoding="utf-8")
    match = re.search(r"const ARTICLES = (\[[\s\S]*?\]);", source)
    if not match:
        raise RuntimeError("Could not find the ARTICLES catalogue in articles.js")
    articles = json.loads(match.group(1))
    if not articles:
        raise RuntimeError("The ARTICLES catalogue is empty")
    return articles


def cards_for(articles: list[dict]) -> str:
    cards: list[str] = []
    for index, article in enumerate(articles[:6]):
        article_slug = html.escape(article.get("slug", ""), quote=True)
        title = html.escape(article.get("title", ""))
        category = html.escape(article.get("category", "Guides"))
        excerpt = html.escape(article.get("excerpt", ""))
        image = "/" + article.get("image", "").lstrip("/")
        alt = html.escape(article.get("alt", title), quote=True)
        loading = 'fetchpriority="high"' if index == 0 else 'loading="lazy"'
        cards.append(
            f'      <article class="card card-featured"><img src="{html.escape(image, quote=True)}" '
            f'alt="{alt}" class="card-featured-img" width="800" height="200" {loading}>'
            f'<div class="card-body"><span class="card-tag">{category}</span>'
            f'<h3><a href="/articles/{article_slug}.html">{title}</a></h3>'
            f'<p>{excerpt}</p><a href="/articles/{article_slug}.html" class="read-more">'
            f'Read article &rarr;</a></div></article>'
        )
    return START + "\n" + "\n".join(cards) + "\n      " + END


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if the homepage cards are stale")
    args = parser.parse_args()

    homepage = HOMEPAGE.read_text(encoding="utf-8")
    replacement = cards_for(load_articles())
    updated, replacements = re.subn(
        re.escape(START) + r"[\s\S]*?" + re.escape(END),
        replacement,
        homepage,
        count=1,
    )
    if replacements != 1:
        raise RuntimeError("Could not find exactly one latest-cards section in index.html")
    if args.check:
        if updated != homepage:
            raise SystemExit("Homepage latest cards are stale")
        print("Homepage latest cards are current")
        return
    if updated != homepage:
        HOMEPAGE.write_text(updated, encoding="utf-8")
        print("Homepage latest cards refreshed")
    else:
        print("Homepage latest cards already current")


if __name__ == "__main__":
    main()
