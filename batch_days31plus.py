"""
NicheHubPro — Days 31-60 Batch Publisher
Expands into: Relationships, Money Stress, Fitness for Mental Health,
Self-Worth, Parenting Burnout, Social Anxiety, Mindfulness, Stress Recovery.

Usage:
  python batch_days31plus.py            <- publish next unpublished day
  python batch_days31plus.py --day 35   <- publish specific day
  python batch_days31plus.py --status   <- show what's done/pending
"""

import sys, os, re, time
sys.stdout.reconfigure(encoding='utf-8')
from publisher_v2 import generate_article

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
TRACKING_FILE = os.path.join(BASE_DIR, "published_days31plus.txt")

PLAN = [

    # ── WEEK 5: Relationships & Boundaries (1/day) ────────────────────────
    (31, [("how to set healthy boundaries",         "boundary setting tips",              "how to set boundaries without feeling guilty",        "Mental Wellness")]),
    (32, [("how to deal with toxic people",         "toxic relationship signs",           "how to protect your energy from toxic people",        "Mental Wellness")]),
    (33, [("how to stop people pleasing",           "people pleaser recovery",            "how to stop being a people pleaser and say no",       "Mental Wellness")]),
    (34, [("how to improve emotional intelligence", "EQ tips for adults",                 "how to develop emotional intelligence in daily life",  "Mental Wellness")]),
    (35, [("how to communicate better in relationships", "communication skills",          "how to communicate your feelings without fighting",   "Mental Wellness")]),

    # ── WEEK 6: Money Stress & Loneliness (1/day) ─────────────────────────
    (36, [("financial anxiety symptoms",            "money stress relief",                "signs you have financial anxiety and how to fix it",  "Mental Wellness")]),
    (37, [("how to stop worrying about money",      "financial stress management",        "how to stop money anxiety and feel financially calm",  "Mental Wellness")]),
    (38, [("how to deal with loneliness",           "loneliness mental health",           "how to feel less lonely and more connected",          "Mental Wellness")]),
    (39, [("how to be more present",                "mindfulness in daily life",          "how to stop living in your head and be more present", "Mental Wellness")]),
    (40, [("how to deal with depression naturally", "natural depression relief",          "natural ways to manage depression at home",           "Mental Wellness")]),

    # ── WEEK 7: Fitness + Physical Mental Health (2/day) ──────────────────
    (41, [
        ("how to start working out for mental health", "exercise for anxiety",           "how exercise helps with anxiety and depression",      "Healthy Lifestyle"),
        ("cold shower benefits for mental health",  "cold shower anxiety",               "how cold showers help with anxiety and stress",       "Healthy Lifestyle"),
    ]),
    (42, [
        ("breathing exercises for anxiety",         "deep breathing techniques",         "best breathing exercises to calm anxiety fast",       "Mental Wellness"),
        ("yoga for stress and anxiety",             "yoga mental health benefits",        "how yoga helps with stress and anxiety relief",       "Healthy Lifestyle"),
    ]),
    (43, [
        ("how to stop being lazy",                  "overcome laziness tips",             "why am I so lazy and how to fix it",                  "Productivity"),
        ("how to wake up early and not feel tired", "early morning tips",                 "how to wake up at 5am and feel energized",            "Healthy Lifestyle"),
    ]),
    (44, [
        ("how to manage work from home burnout",    "remote work stress",                 "signs of work from home burnout and how to recover",  "Mental Wellness"),
        ("how to disconnect from work",             "work life balance tips",             "how to stop thinking about work after hours",         "Healthy Lifestyle"),
    ]),
    (45, [
        ("how to improve self-esteem",              "low self esteem causes",             "how to improve low self esteem and feel better",      "Mental Wellness"),
        ("how to stop comparing yourself to others","comparison anxiety",                 "how to stop comparing yourself and be happy",         "Mental Wellness"),
    ]),

    # ── WEEK 8: Identity + Social Anxiety (3/day) ─────────────────────────
    (46, [
        ("how to deal with impostor syndrome",      "impostor syndrome at work",         "how to overcome impostor syndrome and self doubt",    "Mental Wellness"),
        ("how to stop procrastinating immediately", "beat procrastination now",           "how to stop procrastinating right now in 5 minutes",  "Productivity"),
        ("how to detox from social media",          "social media mental health",         "how to take a social media detox and feel better",    "Healthy Lifestyle"),
    ]),
    (47, [
        ("parenting burnout symptoms",              "parent mental health",               "signs of parenting burnout and how to recover",       "Mental Wellness"),
        ("how to be a calm parent",                 "calm parenting techniques",          "how to stay calm as a parent when overwhelmed",       "Mental Wellness"),
        ("how to reduce mom guilt",                 "mom guilt relief",                   "how to stop mom guilt and be a happier parent",       "Mental Wellness"),
    ]),
    (48, [
        ("how to build mental resilience",          "resilience building tips",           "how to build mental toughness and resilience",        "Mental Wellness"),
        ("how to overcome fear",                    "fear management techniques",         "how to face your fears and stop letting fear win",    "Mental Wellness"),
        ("how to be more confident socially",       "social confidence tips",             "how to feel more confident in social situations",     "Mental Wellness"),
    ]),
    (49, [
        ("how to deal with work stress",            "workplace stress relief",            "how to manage stress at work without burning out",    "Mental Wellness"),
        ("how to set work life boundaries",         "work boundaries tips",               "how to create healthy boundaries between work and life","Productivity"),
        ("how to unwind after work",                "after work relaxation",              "best ways to unwind and decompress after work",       "Healthy Lifestyle"),
    ]),
    (50, [
        ("how to overcome social anxiety",          "social anxiety relief",              "how to overcome social anxiety in everyday situations","Mental Wellness"),
        ("how to make friends as an adult",         "adult friendship tips",              "how to make new friends as an adult without effort",  "Mental Wellness"),
        ("how to feel less alone",                  "combat loneliness tips",             "how to feel less alone and more connected to others",  "Mental Wellness"),
    ]),

    # ── WEEK 9: Mindfulness + Journaling (3/day) ──────────────────────────
    (51, [
        ("how to find motivation when depressed",   "motivation depression tips",         "how to get motivated when you feel depressed",        "Mental Wellness"),
        ("how to get out of a rut",                 "life rut recovery",                  "how to get out of a life rut and start fresh",        "Mental Wellness"),
        ("how to restart your life",                "fresh start tips",                   "how to start over and rebuild your life step by step", "Mental Wellness"),
    ]),
    (52, [
        ("how to journal for mental health",        "journaling mental health tips",      "how to start journaling for anxiety and stress",      "Mental Wellness"),
        ("gratitude practice benefits",             "daily gratitude tips",               "how daily gratitude changes your brain and mood",     "Mental Wellness"),
        ("mindfulness for beginners",               "how to practice mindfulness",        "how to start mindfulness practice for beginners",     "Mental Wellness"),
    ]),
    (53, [
        ("how to manage chronic stress",            "long term stress management",        "how to manage chronic stress without medication",     "Mental Wellness"),
        ("how to lower cortisol naturally",         "cortisol reduction tips",            "natural ways to lower cortisol and reduce stress",    "Healthy Lifestyle"),
        ("adrenal fatigue recovery",                "adrenal fatigue symptoms",           "how to recover from adrenal fatigue naturally",       "Healthy Lifestyle"),
    ]),
    (54, [
        ("how to build a night routine",            "evening routine for sleep",          "best night routine for better sleep and mental health","Healthy Lifestyle"),
        ("how to sleep without anxiety",            "sleep anxiety relief",               "how to fall asleep when anxiety keeps you awake",     "Mental Wellness"),
        ("how to wake up refreshed",                "wake up energized tips",             "how to wake up feeling refreshed and not tired",      "Healthy Lifestyle"),
    ]),
    (55, [
        ("how to be more productive working from home", "remote work productivity",      "how to stay productive and focused working from home","Productivity"),
        ("best productivity apps",                  "top productivity tools",             "best apps to help you focus and be more productive",  "Productivity"),
        ("morning productivity routine",            "productive morning habits",          "how to create a morning routine that makes you productive","Productivity"),
    ]),

    # ── WEEK 10: Self-Compassion + Life Goals (3/day) ─────────────────────
    (56, [
        ("how to stop self-sabotage",               "self sabotage patterns",             "why do I self sabotage and how to stop it",           "Mental Wellness"),
        ("how to overcome self-doubt",              "beat self doubt tips",               "how to stop doubting yourself and build confidence",  "Mental Wellness"),
        ("how to be kinder to yourself",            "self compassion tips",               "how to treat yourself with more kindness every day",  "Mental Wellness"),
    ]),
    (57, [
        ("how to practice self-compassion",         "self compassion exercises",          "how to develop self compassion when you are hard on yourself","Mental Wellness"),
        ("how to let go of the past",               "letting go techniques",              "how to let go of past mistakes and move forward",     "Mental Wellness"),
        ("how to forgive yourself",                 "self forgiveness guide",             "how to forgive yourself for past mistakes and heal",  "Mental Wellness"),
    ]),
    (58, [
        ("how to stop emotional eating",            "emotional eating help",              "how to stop emotional eating and manage food cravings","Healthy Lifestyle"),
        ("mindful eating tips",                     "mindful eating for beginners",       "how to practice mindful eating to stop overeating",   "Healthy Lifestyle"),
        ("how to build a healthy relationship with food", "food relationship tips",       "how to heal your relationship with food and your body","Healthy Lifestyle"),
    ]),
    (59, [
        ("how to build healthy relationships",      "healthy relationship tips",          "what makes a healthy relationship and how to build one","Mental Wellness"),
        ("how to maintain friendships",             "keep friendships strong",            "how to maintain friendships as a busy adult",         "Mental Wellness"),
        ("how to improve communication skills",     "communication improvement",          "how to become a better communicator in all areas of life","Mental Wellness"),
    ]),
    (60, [
        ("how to create a vision for your life",    "life vision tips",                   "how to create a clear vision for your future life",   "Mental Wellness"),
        ("how to set realistic goals",              "goal setting guide",                 "how to set goals you will actually achieve",          "Productivity"),
        ("how to stay consistent",                  "consistency habits",                 "how to stay consistent and not give up on your goals","Productivity"),
    ]),
]

TOTAL_ARTICLES = sum(len(articles) for _, articles in PLAN)


def load_published():
    articles_js = os.path.join(BASE_DIR, "articles.js")
    existing_slugs = set()
    if os.path.exists(articles_js):
        import json, re as _re
        with open(articles_js, "r", encoding="utf-8") as f:
            content = f.read()
        m = _re.search(r'const ARTICLES = (\[[\s\S]*?\]);', content)
        if m:
            try:
                arts = json.loads(m.group(1))
                existing_slugs = {a["slug"] for a in arts}
            except Exception:
                pass
    published = set()
    for day, day_articles in PLAN:
        day_slugs = {re.sub(r'[^a-z0-9]+', '-', kw.lower()).strip('-')[:60]
                     for kw, _, _, _ in day_articles}
        if day_slugs.issubset(existing_slugs):
            published.add(day)
    return published


def mark_published(day):
    with open(TRACKING_FILE, "a", encoding="utf-8") as f:
        f.write(str(day) + "\n")


def show_status():
    published = load_published()
    total_done = sum(len(a) for d, a in PLAN if d in published)
    print(f"\n{'='*65}")
    print(f"  DAYS 31-60 STATUS  ({total_done}/{TOTAL_ARTICLES} articles)")
    print(f"{'='*65}")
    for day, articles in PLAN:
        status = "✅" if day in published else "⏳"
        count  = f"({len(articles)} article{'s' if len(articles)>1 else ''})"
        print(f"  {status} Day {day:02d} {count}")
        for primary, _, _, category in articles:
            print(f"         [{category[:14]:14}] {primary}")
    print(f"\n  Done: {len(published)}/30  |  Remaining: {30-len(published)}/30")
    print(f"{'='*65}\n")


def run_day(day_num):
    entry = next((d for d in PLAN if d[0] == day_num), None)
    if not entry:
        print(f"Day {day_num} not in plan.")
        return False
    _, articles = entry
    print(f"\n{'='*65}\n  DAY {day_num} — {len(articles)} article(s)\n{'='*65}")
    success = 0
    for i, (primary, secondary, longtail, category) in enumerate(articles, 1):
        if len(articles) > 1:
            print(f"\n  [{i}/{len(articles)}] {primary}")
        result = generate_article(primary, secondary, longtail, category)
        if result:
            success += 1
        if i < len(articles):
            time.sleep(2)
    if success > 0:
        mark_published(day_num)
        print(f"\n  Day {day_num} complete: {success}/{len(articles)} published.")
        return True
    return False


def main():
    args = sys.argv[1:]
    if "--status" in args:
        show_status(); return
    if "--day" in args:
        idx = args.index("--day")
        run_day(int(args[idx + 1])); return
    published = load_published()
    next_entry = next((d for d in PLAN if d[0] not in published), None)
    if not next_entry:
        print("All 30 days (31-60) published!"); show_status(); return
    day_num, articles = next_entry
    print(f"Publishing Day {day_num}: {len(articles)} article(s)")
    run_day(day_num)


if __name__ == "__main__":
    main()
