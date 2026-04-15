"""
NicheHubPro — Pinterest Auto-Publisher
Creates a pin for each published article on the matching board.

Usage:
  python pinterest_publisher.py                  <- pin latest unpinned article
  python pinterest_publisher.py --all            <- pin all articles not yet pinned
  python pinterest_publisher.py --slug how-to-stop-overthinking
"""

import sys, os, json, re, requests
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
SITE_URL   = "https://nichehubpro.com"
API_BASE   = "https://api.pinterest.com/v5"
PINS_LOG   = os.path.join(BASE_DIR, "pinterest_pins.csv")  # gitignored

# ── LOAD TOKEN ────────────────────────────────────────────────────────────────
try:
    from config import PINTEREST_ACCESS_TOKEN
except ImportError:
    PINTEREST_ACCESS_TOKEN = os.environ.get("PINTEREST_ACCESS_TOKEN", "")

HEADERS = {
    "Authorization": f"Bearer {PINTEREST_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# ── BOARD MAP (category → board ID) ───────────────────────────────────────────
# Populated after boards are created on Pinterest
BOARD_IDS = {
    "Mental Wellness":   "",   # fill after creating boards
    "Productivity":      "",
    "Healthy Lifestyle": "",
}

# ── LOAD ARTICLES ─────────────────────────────────────────────────────────────
def load_articles():
    path = os.path.join(BASE_DIR, "articles.js")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    m = re.search(r'const ARTICLES = (\[[\s\S]*?\]);', content)
    if not m:
        return []
    return json.loads(m.group(1))


# ── LOAD PINNED LOG ───────────────────────────────────────────────────────────
def load_pinned_slugs():
    if not os.path.exists(PINS_LOG):
        return set()
    with open(PINS_LOG, "r", encoding="utf-8") as f:
        return {line.strip().split(",")[0] for line in f if line.strip()}


def mark_pinned(slug, pin_id):
    with open(PINS_LOG, "a", encoding="utf-8") as f:
        f.write(f"{slug},{pin_id}\n")


# ── GET BOARDS ────────────────────────────────────────────────────────────────
def fetch_boards():
    resp = requests.get(f"{API_BASE}/boards", headers=HEADERS)
    if resp.status_code == 200:
        return resp.json().get("items", [])
    print(f"  Error fetching boards: {resp.status_code} {resp.text}")
    return []


def auto_fill_board_ids():
    """Automatically match boards by name to BOARD_IDS."""
    boards = fetch_boards()
    for board in boards:
        name = board.get("name", "")
        if name in BOARD_IDS:
            BOARD_IDS[name] = board["id"]
            print(f"  Board matched: {name} → {board['id']}")


# ── CREATE PIN ────────────────────────────────────────────────────────────────
def create_pin(article, pin_data=None):
    """
    Create a single pin. If pin_data is provided (title + description from articles.js),
    use it; otherwise fall back to a generic pin from the article excerpt.
    """
    category  = article.get("category", "Mental Wellness")
    board_id  = BOARD_IDS.get(category, "")

    if not board_id:
        print(f"  No board ID for category: {category}. Skipping.")
        return None

    slug      = article["slug"]
    image_url = f"{SITE_URL}/{article['image']}"
    link      = f"{SITE_URL}/articles/{slug}.html"
    alt_text  = article.get("alt", article["title"])

    if pin_data:
        title       = pin_data.get("title", article["title"])[:100]
        description = pin_data.get("description", "")[:500]
        if link not in description:
            description += f"\n\nRead more: {link}"
    else:
        title       = article["title"]
        excerpt     = article.get("excerpt", "")[:400]
        description = f"{excerpt}\n\nRead the full guide: {link}\n\n#MentalWellness #Wellness #NicheHubPro"

    payload = {
        "board_id": board_id,
        "title": title,
        "description": description,
        "link": link,
        "media_source": {
            "source_type": "image_url",
            "url": image_url
        },
        "alt_text": alt_text
    }

    resp = requests.post(f"{API_BASE}/pins", headers=HEADERS, json=payload)

    if resp.status_code in (200, 201):
        pin_id = resp.json().get("id", "unknown")
        print(f"    Pin created: {title[:55]} → {pin_id}")
        return pin_id
    else:
        print(f"    Pin failed ({resp.status_code}): {resp.text[:200]}")
        return None


def create_all_pins_for_article(article):
    """Create up to 3 pins for one article using pins data from articles.js."""
    pins_data = article.get("pins", [])
    slug      = article["slug"]

    if pins_data:
        print(f"  Creating {len(pins_data)} pin(s) for: {article['title'][:55]}")
        created = 0
        for i, pin_data in enumerate(pins_data[:3], 1):
            print(f"    Pin {i}/{len(pins_data[:3])}...")
            pin_id = create_pin(article, pin_data)
            if pin_id:
                mark_pinned(slug, pin_id)
                created += 1
        return created
    else:
        # Fallback: one generic pin (older articles without pins data)
        print(f"  No pin data — creating 1 generic pin for: {article['title'][:55]}")
        pin_id = create_pin(article)
        if pin_id:
            mark_pinned(slug, pin_id)
            return 1
        return 0


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    args = sys.argv[1:]

    if not PINTEREST_ACCESS_TOKEN:
        print("ERROR: PINTEREST_ACCESS_TOKEN not set in config.py or environment.")
        sys.exit(1)

    print("Fetching Pinterest boards...")
    auto_fill_board_ids()

    missing = [k for k, v in BOARD_IDS.items() if not v]
    if missing:
        print(f"  WARNING: No board found for: {missing}")
        print(f"  Create these boards on Pinterest first.")

    articles = load_articles()
    pinned   = load_pinned_slugs()

    # An article is "fully pinned" when its slug appears 3 times in the log
    pin_counts = {}
    for s in pinned:
        pin_counts[s] = pin_counts.get(s, 0) + 1

    if "--all" in args:
        to_pin = [a for a in articles if pin_counts.get(a["slug"], 0) == 0]
    elif "--slug" in args:
        idx = args.index("--slug")
        target = args[idx + 1]
        to_pin = [a for a in articles if a["slug"] == target]
    else:
        # Default: pin latest unpinned article only
        to_pin = [a for a in articles if pin_counts.get(a["slug"], 0) == 0][:1]

    if not to_pin:
        print("No new articles to pin.")
        return

    print(f"\nPinning {len(to_pin)} article(s)...")
    total_pins = 0
    for article in to_pin:
        print(f"\n  [{article['category']}] {article['title'][:60]}")
        total_pins += create_all_pins_for_article(article)

    print(f"\nDone. {total_pins} pin(s) created.")


if __name__ == "__main__":
    main()
