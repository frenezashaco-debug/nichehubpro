"""Create a repeatable, evidence-focused quality queue for NicheHubPro.

This tool deliberately reports risks instead of rewriting claims automatically.
Health and wellbeing claims require an editor to verify both the wording and its
supporting source before publication. The CSV gives the editorial team one
prioritized batch rather than a collection of one-off checks.
"""

from __future__ import annotations

import csv
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).parent
ARTICLES = ROOT / "articles"
REPORTS = ROOT / "reports"
sys.stdout.reconfigure(encoding="utf-8")

NAMED_SOURCES = re.compile(
    r"\b(?:APA|American Psychological Association|Harvard(?: Health)?|"
    r"Mayo Clinic|Stanford(?: University)?|Cleveland Clinic|"
    r"National Sleep Foundation|University College London|CDC|NIMH)\b",
    re.I,
)
UNSUPPORTED_EVIDENCE = re.compile(
    r"\b(?:research|stud(?:y|ies))\s+(?:shows?|found|proves?)\b", re.I
)
PRECISE_CLAIM = re.compile(r"\b(?:\d{1,3}%|\d+(?:\.\d+)?\s*(?:minutes?|hours?|days?))\b", re.I)
MEDICAL_ABSOLUTE = re.compile(r"\b(?:cure(?:s|d)?|reverse(?:s|d)?|guarantee(?:s|d)?)\b", re.I)
HOME_PAGE = re.compile(r"^https://[^/]+/?(?:\?.*)?$")


def visible_text(markup: str) -> str:
    without_code = re.sub(
        r"<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>",
        " ",
        markup,
        flags=re.I | re.S,
    )
    return html.unescape(re.sub(r"<[^>]+>", " ", without_code))


def meta(markup: str, name: str) -> str:
    pattern = rf'<meta[^>]+(?:name|property)=["\']{re.escape(name)}["\'][^>]+content=["\']([^"\']*)'
    match = re.search(pattern, markup, re.I)
    return html.unescape(match.group(1).strip()) if match else ""


def canonical(markup: str) -> str:
    match = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)', markup, re.I)
    return match.group(1).strip() if match else ""


def external_urls(markup: str) -> list[str]:
    urls = re.findall(r'<a\b[^>]+href=["\'](https://[^"\']+)', markup, re.I)
    return sorted(set(urls))


def broken_local_targets(markup: str) -> tuple[int, int]:
    """Return missing article links and missing local image assets."""
    missing_articles = 0
    missing_images = 0
    for href in re.findall(r'href=["\'](?:\.\./|/)?articles/([^"\'#?]+\.html)', markup, re.I):
        if not (ARTICLES / Path(href).name).exists():
            missing_articles += 1
    for src in re.findall(r'src=["\'](?:\.\./|/)?images/([^"\'#?]+)', markup, re.I):
        if not (ROOT / "images" / Path(src).name).exists():
            missing_images += 1
    return missing_articles, missing_images


def article_row(path: Path) -> dict[str, object]:
    markup = path.read_text(encoding="utf-8")
    text = visible_text(markup)
    urls = external_urls(markup)
    source_urls = [url for url in urls if urlparse(url).netloc not in {"play.google.com", "www.pinterest.com"}]
    homepages = [url for url in source_urls if HOME_PAGE.match(url)]
    # WHO is deliberately handled case-sensitively. With a case-insensitive
    # pattern, ordinary uses of the word "who" became false institutional hits.
    named_mentions = len(NAMED_SOURCES.findall(text)) + len(re.findall(r"\bWHO\b", text))
    unsupported = len(UNSUPPORTED_EVIDENCE.findall(text))
    precise = len(PRECISE_CLAIM.findall(text))
    absolutes = len(MEDICAL_ABSOLUTE.findall(text))
    missing_articles, missing_images = broken_local_targets(markup)
    word_count = len(re.findall(r"\b[\w'-]+\b", text))
    title_match = re.search(r"<title>(.*?)</title>", markup, re.I | re.S)
    title = html.unescape(re.sub(r"\s+", " ", title_match.group(1)).strip()) if title_match else ""
    description = meta(markup, "description")
    canonical_url = canonical(markup)
    risk = (len(homepages) * 5) + (named_mentions * 2) + (unsupported * 2) + precise + (absolutes * 3)
    issues = []
    if not title:
        issues.append("missing title")
    if not description:
        issues.append("missing meta description")
    if not canonical_url:
        issues.append("missing canonical")
    if word_count < 800:
        issues.append("thin content")
        risk += 8
    if homepages:
        issues.append(f"{len(homepages)} homepage source link(s)")
    if named_mentions:
        issues.append(f"{named_mentions} named institution mention(s)")
    if unsupported:
        issues.append(f"{unsupported} evidence claim(s) needing verification")
    if precise:
        issues.append(f"{precise} precise number(s) needing verification")
    if absolutes:
        issues.append(f"{absolutes} absolute claim(s)")
    if missing_articles:
        issues.append(f"{missing_articles} broken internal article link(s)")
        risk += missing_articles * 8
    if missing_images:
        issues.append(f"{missing_images} missing local image asset(s)")
        risk += missing_images * 6
    return {
        "file": path.name,
        "canonical": canonical_url,
        "title": title,
        "words": word_count,
        "risk_score": risk,
        "homepage_sources": len(homepages),
        "named_source_mentions": named_mentions,
        "evidence_claims": unsupported,
        "precise_claims": precise,
        "absolute_claims": absolutes,
        "broken_article_links": missing_articles,
        "missing_image_assets": missing_images,
        "issues": "; ".join(issues) or "No automated risk flag",
    }


def main() -> None:
    rows = [article_row(path) for path in sorted(ARTICLES.glob("*.html"))]
    rows.sort(key=lambda row: (-int(row["risk_score"]), str(row["file"])))
    REPORTS.mkdir(exist_ok=True)
    fields = list(rows[0]) if rows else []
    with (REPORTS / "editorial-review-queue.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "articles": len(rows),
        "articles_needing_review": sum(1 for row in rows if int(row["risk_score"]) > 0),
        "top_25": rows[:25],
        "totals": {
            key: sum(int(row[key]) for row in rows)
            for key in (
                "homepage_sources", "named_source_mentions", "evidence_claims",
                "precise_claims", "absolute_claims", "broken_article_links", "missing_image_assets",
            )
        },
    }
    (REPORTS / "editorial-review-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Audited {len(rows)} articles.")
    print(f"Articles needing review: {summary['articles_needing_review']}")
    print("Top 15 review priorities:")
    for row in rows[:15]:
        print(f"- {row['risk_score']:>3} {row['file']}: {row['issues']}")


if __name__ == "__main__":
    main()
