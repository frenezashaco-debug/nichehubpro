"""
NicheHubPro — 30-Day Batch Publisher (Final Plan)
Supports multiple articles per day (Week 3: 3/day, Week 4: 3/day).

Usage:
  python batch_30days.py           <- publish next unpublished day
  python batch_30days.py --day 5   <- publish specific day
  python batch_30days.py --status  <- show what's done/pending
"""

import sys, os, re, time, json
sys.stdout.reconfigure(encoding='utf-8')
from publisher_v2 import generate_article

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
TRACKING_FILE = os.path.join(BASE_DIR, "published_30days.txt")

# ── FINAL 30-DAY KEYWORD PLAN ─────────────────────────────────────────────
# Format: (day, [ (primary, secondary, longtail, category), ... ])
# Week 1-2: 1 article/day | Week 3: 3/day | Week 4: 3/day

PLAN = [

    # ── WEEK 1: Overthinking + Anxiety Core (1 article/day) ──────────────
    (1, [
        ("how to stop overthinking",           "overthinking at night",              "why do I overthink everything",                      "Mental Wellness"),
    ]),
    (2, [
        ("how to calm anxiety quickly",        "anxiety in the morning",             "how to calm anxiety in 5 minutes",                   "Mental Wellness"),
    ]),
    (3, [
        ("signs of mental exhaustion",         "burnout symptoms mental",            "how do I know if I am mentally exhausted",            "Mental Wellness"),
    ]),
    (4, [
        ("how to stop negative thoughts",      "negative thinking patterns",         "why do I always think negatively",                   "Mental Wellness"),
    ]),
    (5, [
        ("how to reduce stress naturally",     "natural stress relief methods",      "what reduces stress quickly at home",                 "Mental Wellness"),
    ]),
    (6, [
        ("how to relax your mind",             "mental relaxation techniques",       "how to relax your brain fast",                       "Mental Wellness"),
    ]),
    (7, [
        ("how to deal with anxiety daily",     "daily anxiety management",           "how to live with anxiety everyday",                  "Mental Wellness"),
    ]),

    # ── WEEK 2: Deep Anxiety + Control Mind (1 article/day) ──────────────
    (8, [
        ("how to stop anxiety attacks",        "panic attack help",                  "what to do during a panic attack",                   "Mental Wellness"),
    ]),
    (9, [
        ("how to control your thoughts",       "intrusive thoughts",                 "why can't I control my thoughts",                    "Mental Wellness"),
    ]),
    (10, [
        ("how to calm your mind instantly",    "instant relaxation techniques",      "how to relax your mind quickly",                     "Mental Wellness"),
    ]),
    (11, [
        ("how to stop worrying",               "excessive worrying causes",          "how to stop worrying about everything",              "Mental Wellness"),
    ]),
    (12, [
        ("how to improve mental clarity",      "brain fog solutions",                "why can't I think clearly",                          "Mental Wellness"),
    ]),
    (13, [
        ("how to feel calm instantly",         "calm your mind fast",                "how to relax in stressful situations",               "Mental Wellness"),
    ]),
    (14, [
        ("how to feel happy again",            "happiness habits",                   "why do I feel unhappy for no reason",                "Mental Wellness"),
    ]),

    # ── WEEK 3: Expansion (2 Mental + 1 Lifestyle per day) ───────────────
    (15, [
        ("how to stop overthinking at work",   "stress at work solutions",           "how to stop overthinking at work and focus",         "Mental Wellness"),
        ("morning routine for mental health",  "healthy morning habits",             "what is the best morning routine for mental health", "Healthy Lifestyle"),
    ]),
    (16, [
        ("anxiety before sleep",               "racing thoughts at night",           "how to stop anxiety before sleep",                   "Mental Wellness"),
        ("how to sleep better naturally",      "improve sleep quality",              "how to fall asleep faster naturally",                "Healthy Lifestyle"),
    ]),
    (17, [
        ("fear of failure anxiety",            "performance anxiety",                "how to overcome fear of failure and anxiety",        "Mental Wellness"),
        ("foods that reduce anxiety",          "diet for anxiety",                   "what foods help reduce anxiety naturally",           "Healthy Lifestyle"),
    ]),
    (18, [
        ("how to break negative thinking",     "stop self doubt",                    "how to break negative thinking patterns",            "Mental Wellness"),
        ("how to increase energy naturally",   "natural energy boosters",            "why do I feel tired all the time",                   "Healthy Lifestyle"),
    ]),
    (19, [
        ("how to feel in control of your mind","mental discipline",                  "how to gain control of your thoughts and mind",      "Mental Wellness"),
        ("benefits of walking daily",          "walking for mental health",          "does walking help with anxiety and stress",          "Healthy Lifestyle"),
    ]),
    (20, [
        ("emotional burnout recovery",         "how to recover mentally",            "how to recover from emotional burnout fast",         "Mental Wellness"),
        ("how to detox your mind",             "mental detox techniques",            "how to clear your mind from negative thoughts",      "Mental Wellness"),
    ]),
    (21, [
        ("how to stay calm under pressure",    "stress control techniques",          "how to stay calm in stressful situations",           "Mental Wellness"),
        ("healthy daily habits",               "simple healthy habits",              "what are the best healthy daily habits",             "Healthy Lifestyle"),
    ]),

    # ── WEEK 4: Full Power (1 Mental + 1 Productivity + 1 Lifestyle/day) ─
    (22, [
        ("signs of anxiety disorder",          "anxiety symptoms list",              "what are the signs of anxiety disorder",             "Mental Wellness"),
        ("how to focus without distractions",  "improve focus fast",                 "how to focus without distractions at home",          "Productivity"),
        ("simple morning habits",              "morning routine tips",               "what are the best simple morning habits",            "Healthy Lifestyle"),
    ]),
    (23, [
        ("how to stop panic attacks",          "panic attack control techniques",    "what to do during a panic attack",                  "Mental Wellness"),
        ("how to stop procrastination",        "procrastination tips",               "why do I procrastinate so much",                     "Productivity"),
        ("sleep routine tips",                 "better sleep habits",                "how to create a sleep routine for better sleep",     "Healthy Lifestyle"),
    ]),
    (24, [
        ("how to build confidence",            "confidence building tips",           "how to build self confidence fast",                  "Mental Wellness"),
        ("how to stay motivated",              "motivation tips daily",              "how to stay motivated every day",                    "Productivity"),
        ("healthy lifestyle tips",             "healthy living habits",              "what are the best healthy lifestyle tips",           "Healthy Lifestyle"),
    ]),
    (25, [
        ("how to stop worrying about the future", "stop excessive worrying",         "how to stop worrying about things you can't control","Mental Wellness"),
        ("time management tips",               "manage time better",                 "how to manage time better every day",                "Productivity"),
        ("daily wellness habits",              "wellness routine tips",              "what are the best daily wellness habits",            "Healthy Lifestyle"),
    ]),
    (26, [
        ("how to improve mental clarity",      "brain fog solutions",                "how to improve mental clarity and focus fast",       "Mental Wellness"),
        ("deep work techniques",               "how to do deep work",                "how to do deep work and focus for hours",            "Productivity"),
        ("natural energy boosters",            "increase energy naturally",          "how to boost energy naturally without caffeine",     "Healthy Lifestyle"),
    ]),
    (27, [
        ("how to feel happy again",            "happiness tips simple",              "how to feel happy again when you are sad",           "Mental Wellness"),
        ("how to build discipline",            "self discipline habits",             "how to build self discipline every day",             "Productivity"),
        ("daily self-care routine",            "self care tips",                     "what is the best daily self care routine",          "Healthy Lifestyle"),
    ]),
    (28, [
        ("how to reset your life",             "life reset plan",                    "how to start over and reset your life",              "Mental Wellness"),
        ("productivity system",                "how to be more productive",          "what is the best productivity system",               "Productivity"),
        ("life balance habits",                "work life balance tips",             "how to balance work and personal life",              "Healthy Lifestyle"),
    ]),
    (29, [
        ("how to change your mindset",         "mindset change tips",                "how to change your mindset and thinking",            "Mental Wellness"),
        ("habit building system",              "how to build good habits",           "how to build good habits that stick",                "Productivity"),
        ("improve daily routine",              "better daily routine",               "how to improve your daily routine for success",      "Healthy Lifestyle"),
    ]),
    (30, [
        ("how to improve your life",           "self improvement tips",              "how to improve yourself every day",                  "Mental Wellness"),
        ("success habits",                     "habits of successful people",        "what are the habits of highly successful people",    "Productivity"),
        ("healthy living tips",                "healthy lifestyle habits",           "how to live a healthy lifestyle every day",          "Healthy Lifestyle"),
    ]),
]

# Total articles count
TOTAL_ARTICLES = sum(len(articles) for _, articles in PLAN)


def load_published():
    """Determine published days by checking articles.js slugs — works locally and on CI."""
    articles_js = os.path.join(BASE_DIR, "articles.js")
    published = set()
    existing_slugs = set()

    if os.path.exists(articles_js):
        with open(articles_js, "r", encoding="utf-8") as f:
            content = f.read()
        m = re.search(r'const ARTICLES = (\[[\s\S]*?\]);', content)
        if m:
            try:
                import json
                articles = json.loads(m.group(1))
                existing_slugs = {a["slug"] for a in articles}
            except Exception:
                pass

    for day, day_articles in PLAN:
        day_slugs = {re.sub(r'[^a-z0-9]+', '-', kw.lower()).strip('-')[:60]
                     for kw, _, _, _ in day_articles}
        if day_slugs.issubset(existing_slugs):
            published.add(day)

    return published


def mark_published(day):
    with open(TRACKING_FILE, "a", encoding="utf-8") as f:
        f.write(str(day) + "\n")


def articles_per_day(day_num):
    entry = next((d for d in PLAN if d[0] == day_num), None)
    return len(entry[1]) if entry else 0


def show_status():
    published = load_published()
    total_done = sum(articles_per_day(d) for d in published)
    print(f"\n{'='*65}")
    print(f"  30-DAY PLAN STATUS  ({total_done}/{TOTAL_ARTICLES} articles)")
    print(f"{'='*65}")
    for day, articles in PLAN:
        status = "✅" if day in published else "⏳"
        count  = f"({len(articles)} article{'s' if len(articles) > 1 else ''})"
        print(f"  {status} Day {day:02d} {count}")
        for primary, _, _, category in articles:
            print(f"         [{category[:14]:14}] {primary}")
    print(f"\n  Days done: {len(published)}/30  |  Remaining: {30-len(published)}/30")
    print(f"{'='*65}\n")


def run_day(day_num):
    entry = next((d for d in PLAN if d[0] == day_num), None)
    if not entry:
        print(f"Day {day_num} not found in plan.")
        return False

    _, articles = entry
    print(f"\n{'='*65}")
    print(f"  DAY {day_num} — {len(articles)} article(s)")
    print(f"{'='*65}")

    success_count = 0
    for i, (primary, secondary, longtail, category) in enumerate(articles, 1):
        if len(articles) > 1:
            print(f"\n  [{i}/{len(articles)}] {primary}")
        result = generate_article(primary, secondary, longtail, category)
        if result:
            success_count += 1
        if i < len(articles):
            time.sleep(2)

    if success_count > 0:
        mark_published(day_num)
        print(f"\n  Day {day_num} complete: {success_count}/{len(articles)} articles published.")
        return True
    return False


def main():
    args = sys.argv[1:]

    if "--status" in args:
        show_status()
        return

    if "--day" in args:
        idx = args.index("--day")
        day_num = int(args[idx + 1])
        run_day(day_num)
        return

    # Default: publish next unpublished day
    published = load_published()
    next_entry = next((d for d in PLAN if d[0] not in published), None)
    if not next_entry:
        print("All 30 days published!")
        show_status()
        return

    day_num, articles = next_entry
    print(f"Publishing Day {day_num}: {len(articles)} article(s)")
    run_day(day_num)


if __name__ == "__main__":
    main()
