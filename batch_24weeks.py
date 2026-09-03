"""
NicheHubPro — 24-Week Master Editorial Roadmap (Weeks 13-36 of the site's overall plan)
3 articles/week (Mon/Wed/Fri) | 72 articles total | 24 weeks

Cadence: Monday = Mental Wellness | Wednesday = Productivity | Friday = Healthy Lifestyle

Phases:
  1 (W1-4,   days 1-12)  Build Authority Around Core Problems
  2 (W5-8,   days 13-24) Science-Backed Self-Improvement
  3 (W9-12,  days 25-36) High-Performance Lifestyle
  4 (W13-16, days 37-48) Modern Digital Challenges
  5 (W17-20, days 49-60) Advanced Growth Systems
  6 (W21-24, days 61-72) Pillar Guides & Ecosystem Integration (cornerstone hub content)

Content mix target: ~70% evergreen, ~20% growing trends (concentrated in Phase 4),
~10% cornerstone (concentrated in Phase 6, flagged in CORNERSTONE_DAYS — these
generate as 4500+ word pillar guides via publisher_v2.generate_article(cornerstone=True)).

Usage:
  python batch_24weeks.py             <- show that publishing is paused
  python batch_24weeks.py --day 5     <- show that publishing is paused
  python batch_24weeks.py --status    <- show progress
  python batch_24weeks.py --week 3    <- show week 3 articles
"""

import sys, os, re, time, json
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
TRACKING_FILE = os.path.join(BASE_DIR, "published_24weeks.txt")

# AdSense remediation: automated publishing stays off until every new article
# has a documented human review for sourcing, safety language, and originality.
# Do not remove this guard simply to resume a publishing cadence.
PUBLISHING_PAUSED = True


def make_slug(title):
    """Match the publisher slug format without importing publishing dependencies."""
    value = re.sub(r"[^a-z0-9\s-]", "", title.lower())
    value = re.sub(r"\s+", "-", value.strip())
    return re.sub(r"-+", "-", value)[:60]

# ── 24-WEEK PLAN ────────────────────────────────────────────────────────────
# Format: (day, primary, secondary, longtail, category)
# 3 articles/week = days 1-72. Order per week: Mon (MW) -> Wed (Prod) -> Fri (HL)

PLAN = [

    # ════════════════════════════════════════════════════════════════════════
    # PHASE 1 — Build Authority Around Core Problems (Weeks 13-16 / plan W1-4)
    # ════════════════════════════════════════════════════════════════════════
    # WEEK 1
    (1,  "the emotional root of chronic procrastination", "procrastination and anxiety link",      "why procrastination is really about emotions not laziness",             "Mental Wellness"),
    (2,  "why productivity hacks dont work long term",     "productivity hacks vs real systems",     "why do most productivity hacks stop working after a few weeks",         "Productivity"),
    (3,  "how to build a stress resistant morning routine", "stress resilient daily routine",        "how to design a morning routine that protects you from stress",         "Healthy Lifestyle"),

    # WEEK 2
    (4,  "why chronic stress makes everything feel harder", "chronic stress brain effects",          "how does chronic stress affect your brain and body",                     "Mental Wellness"),
    (5,  "how to protect your focus from constant interruptions", "protecting deep focus",            "how to protect your focus when everyone keeps interrupting you",        "Productivity"),
    (6,  "how to build a routine that survives a busy week", "resilient healthy routine",             "how to stick to healthy habits during a busy or stressful week",        "Healthy Lifestyle"),

    # WEEK 3
    (7,  "how to calm your nervous system fast",            "nervous system regulation techniques",   "how to calm your nervous system when you feel overwhelmed",             "Mental Wellness"),
    (8,  "how to stay focused on hard tasks without burning out", "sustainable focus techniques",     "how to stay focused on difficult tasks without feeling drained",        "Productivity"),
    (9,  "why hydration affects your focus more than you think", "hydration and mental performance",  "how does dehydration affect focus and energy",                           "Healthy Lifestyle"),

    # WEEK 4
    (10, "how to stop feeling guilty for resting",           "rest guilt mental health",              "why do I feel guilty when I rest or do nothing",                         "Mental Wellness"),
    (11, "how to recover focus after a distraction",         "regain focus after interruption",       "how long does it take to refocus after a distraction",                   "Productivity"),
    (12, "how to build energy that lasts all day without crashing", "sustained energy without crash", "how to have consistent energy all day without an afternoon crash",       "Healthy Lifestyle"),

    # ════════════════════════════════════════════════════════════════════════
    # PHASE 2 — Science-Backed Self-Improvement (Weeks 17-20 / plan W5-8)
    # ════════════════════════════════════════════════════════════════════════
    # WEEK 5
    (13, "what neuroplasticity means for changing your habits", "neuroplasticity habit change",       "how does neuroplasticity help you change bad habits",                    "Mental Wellness"),
    (14, "the science of habit formation explained simply", "habit loop science",                     "what does science say about how habits actually form",                  "Productivity"),
    (15, "how your body clock affects when you should exercise", "best time to exercise circadian rhythm", "what is the best time of day to exercise based on your body clock", "Healthy Lifestyle"),

    # WEEK 6
    (16, "how dopamine actually works and why quick fixes backfire", "dopamine and instant gratification", "why do quick dopamine hits make you feel worse long term",         "Mental Wellness"),
    (17, "how to train your brain for longer attention spans", "improve attention span training",     "can you train your brain to have a longer attention span",              "Productivity"),
    (18, "how blood sugar swings affect your energy and mood", "blood sugar energy crashes",           "how do blood sugar spikes and crashes affect your energy",              "Healthy Lifestyle"),

    # WEEK 7
    (19, "what cognitive load does to your decision making", "cognitive load decision fatigue",        "how does mental overload affect the decisions you make",                "Mental Wellness"),
    (20, "the psychology behind why deadlines make you more productive", "deadline psychology productivity", "why do deadlines make people more productive",                 "Productivity"),
    (21, "how sleep debt silently drains your daily performance", "sleep debt effects performance",    "what is sleep debt and how does it affect your daily performance",      "Healthy Lifestyle"),

    # WEEK 8
    (22, "why your brain craves routine even when you resist it", "brain craves routine predictability", "why does the brain prefer routine and predictability",                "Mental Wellness"),
    (23, "how willpower works and why it runs out",          "willpower depletion science",            "why does willpower run out throughout the day",                          "Productivity"),
    (24, "how gut health influences your mood and energy",   "gut brain connection mood",              "how does gut health affect your mood and energy levels",                "Healthy Lifestyle"),

    # ════════════════════════════════════════════════════════════════════════
    # PHASE 3 — High-Performance Lifestyle (Weeks 21-24 / plan W9-12)
    # ════════════════════════════════════════════════════════════════════════
    # WEEK 9
    (25, "how to protect your mental energy like a finite resource", "mental energy management",      "how to manage your mental energy throughout the day",                    "Mental Wellness"),
    (26, "what deep work really requires beyond just focus", "deep work requirements",                "what do you actually need to do real deep work",                         "Productivity"),
    (27, "how to build a recovery routine after high stress days", "stress recovery routine",         "how to recover physically and mentally after a stressful day",           "Healthy Lifestyle"),

    # WEEK 10
    (28, "how to stay emotionally steady during high pressure weeks", "emotional stability under pressure", "how to stay emotionally steady during a high pressure week",       "Mental Wellness"),
    (29, "how to structure your week for maximum energy and output", "weekly energy planning",        "how to plan your week around your energy levels",                        "Productivity"),
    (30, "why active recovery matters more than rest days",  "active recovery benefits",               "is active recovery better than a full rest day",                         "Healthy Lifestyle"),

    # WEEK 11
    (31, "how to build mental stamina for long term goals",  "mental stamina long term goals",         "how to build the mental stamina needed for long term goals",             "Mental Wellness"),
    (32, "how high performers manage energy instead of time", "energy management vs time management", "why do high performers manage energy instead of just time",              "Productivity"),
    (33, "how to eat for sustained energy instead of quick fixes", "nutrition sustained energy",       "what should you eat for energy that actually lasts",                     "Healthy Lifestyle"),

    # WEEK 12
    (34, "how to build resilience before a crisis hits",     "proactive resilience building",          "how to build resilience before you actually need it",                    "Mental Wellness"),
    (35, "how to design daily systems that run without motivation", "systems over motivation",         "how to build daily systems that work even without motivation",           "Productivity"),
    (36, "how to build a lifestyle that supports high performance", "high performance lifestyle habits", "what daily habits support a genuinely high performance lifestyle",     "Healthy Lifestyle"),

    # ════════════════════════════════════════════════════════════════════════
    # PHASE 4 — Modern Digital Challenges (Weeks 25-28 / plan W13-16)
    # ════════════════════════════════════════════════════════════════════════
    # WEEK 13
    (37, "how constant notifications are rewiring your anxiety", "notifications and anxiety",          "how do constant phone notifications affect anxiety levels",              "Mental Wellness"),
    (38, "how to use ai tools without losing your own thinking skills", "ai productivity tools balance", "how to use ai productivity tools without becoming dependent on them",  "Productivity"),
    (39, "how blue light really affects your sleep cycle",   "blue light sleep cycle science",         "does blue light from screens actually disrupt your sleep cycle",         "Healthy Lifestyle"),

    # WEEK 14
    (40, "why information overload leaves you mentally exhausted", "information overload fatigue",     "why does consuming too much information leave you exhausted",           "Mental Wellness"),
    (41, "how to build an ai assisted productivity workflow", "ai productivity workflow setup",        "how to build a daily workflow using ai productivity tools",              "Productivity"),
    (42, "how digital minimalism can improve your daily energy", "digital minimalism benefits",        "can digital minimalism actually improve your energy and mood",           "Healthy Lifestyle"),

    # WEEK 15
    (43, "signs your phone use has become a coping mechanism", "phone use emotional coping",           "how do you know if you use your phone to avoid your feelings",           "Mental Wellness"),
    (44, "how to reclaim focus in a world full of notifications", "focus in distracted world",         "how to stay focused when notifications never stop",                      "Productivity"),
    (45, "how to set boundaries with your phone without extreme rules", "phone boundaries without quitting", "how to set healthy phone boundaries without deleting every app",   "Healthy Lifestyle"),

    # WEEK 16
    (46, "how social comparison online quietly damages self esteem", "social media comparison self esteem", "how does comparing yourself to others online affect self esteem",  "Mental Wellness"),
    (47, "how to design a notification system that protects your focus", "notification management system", "how to set up notifications so they dont destroy your focus",       "Productivity"),
    (48, "how to unplug for a full day without feeling anxious", "digital detox anxiety",              "how to do a full day digital detox without feeling anxious",             "Healthy Lifestyle"),

    # ════════════════════════════════════════════════════════════════════════
    # PHASE 5 — Advanced Growth Systems (Weeks 29-32 / plan W17-20)
    # ════════════════════════════════════════════════════════════════════════
    # WEEK 17
    (49, "why overthinking decisions leads to worse outcomes", "decision overthinking outcomes",       "does overthinking a decision actually lead to worse outcomes",           "Mental Wellness"),
    (50, "how to build a personal system for making better decisions", "decision making framework",   "how to create a simple framework for making better decisions",           "Productivity"),
    (51, "how to build sustainable discipline without burning out", "sustainable discipline without burnout", "how to stay disciplined with your health habits without burning out", "Healthy Lifestyle"),

    # WEEK 18
    (52, "how habit architecture shapes your identity over time", "habit architecture identity",       "how do your daily habits shape who you become over time",                "Mental Wellness"),
    (53, "how to architect your habits instead of relying on willpower", "habit architecture design", "how to design your environment so good habits happen automatically",     "Productivity"),
    (54, "how to build a personal system for tracking your health", "personal health tracking system", "how to build a simple system to track your health long term",           "Healthy Lifestyle"),

    # WEEK 19
    (55, "why resilience is a skill you can train not a trait", "resilience as trainable skill",       "is resilience something you are born with or can you train it",         "Mental Wellness"),
    (56, "how to build a personal system for weekly reflection", "weekly reflection system",           "how to set up a simple weekly reflection practice that sticks",          "Productivity"),
    (57, "how to build long term discipline around your health without perfectionism", "flexible discipline health habits", "how to stay consistent with health habits without being perfect", "Healthy Lifestyle"),

    # WEEK 20
    (58, "how to make hard decisions when you feel stuck",   "decision making when stuck",             "how to make a hard decision when you feel completely stuck",             "Mental Wellness"),
    (59, "how to build systems that compound your progress over time", "compounding systems progress", "how to build daily systems whose results compound over time",           "Productivity"),
    (60, "how to build resilience into your daily health routine", "resilient health routine",          "how to build a health routine that survives setbacks and bad weeks",     "Healthy Lifestyle"),

    # ════════════════════════════════════════════════════════════════════════
    # PHASE 6 — Pillar Guides & Ecosystem Integration (Weeks 33-36 / plan W21-24)
    # Days marked CORNERSTONE below generate as 4500+ word flagship guides.
    # ════════════════════════════════════════════════════════════════════════
    # WEEK 21 — the 3 flagship pillar guides (CORNERSTONE)
    (61, "the ultimate guide to building unshakable mental discipline", "complete guide mental discipline", "what does it really take to build unshakable mental discipline", "Mental Wellness"),
    (62, "the complete productivity handbook for a distracted world", "productivity handbook guide",   "what is the best complete system for staying productive today",          "Productivity"),
    (63, "the healthy lifestyle blueprint for lasting energy and balance", "healthy lifestyle blueprint guide", "what is a complete blueprint for a genuinely healthy lifestyle",  "Healthy Lifestyle"),

    # WEEK 22 — supporting hubs linking back to the pillars
    (64, "how all the pieces of mental resilience fit together", "mental resilience complete framework", "how do focus, discipline, and resilience work together for mental strength", "Mental Wellness"),
    (65, "how to combine deep work, systems, and discipline into one workflow", "combined productivity workflow", "how to combine different productivity methods into one simple workflow", "Productivity"),
    (66, "how to combine sleep, nutrition, and movement into one daily system", "combined wellness daily system", "how to combine sleep, food, and movement into one simple daily system",  "Healthy Lifestyle"),

    # WEEK 23 — second wave of cornerstone guides
    (67, "a complete framework for handling any high stress situation", "high stress situation framework", "what is a step by step framework for handling high stress moments",   "Mental Wellness"),
    (68, "how to build a personal operating system for your entire week", "weekly personal operating system", "how to design a personal operating system that runs your whole week", "Productivity"),
    (69, "a complete guide to building energy that lasts a lifetime", "lifetime energy guide",          "what habits actually build energy that lasts for years not days",        "Healthy Lifestyle"),

    # WEEK 24 — final synthesis week
    (70, "how to turn everything you have learned into lasting change", "lasting personal change synthesis", "how do you turn self improvement knowledge into real lasting change", "Mental Wellness"),
    (71, "the daily productivity checklist that ties everything together", "complete daily productivity checklist", "what is a complete daily checklist for staying productive and focused", "Productivity"),
    (72, "how to design a life that supports your long term wellbeing", "life design long term wellbeing", "how to design your daily life around long term wellbeing not quick fixes", "Healthy Lifestyle"),
]

# Cornerstone / pillar days — generated as 4500+ word flagship guides (~10% of plan)
CORNERSTONE_DAYS = {61, 62, 63, 67, 68, 69, 72}

TOTAL_ARTICLES = len(PLAN)
TOTAL_WEEKS    = 24
ARTICLES_PER_WEEK = 3


def load_published():
    """Check which days are done by comparing articles.js slugs."""
    articles_js = os.path.join(BASE_DIR, "articles.js")
    existing_slugs = set()
    if os.path.exists(articles_js):
        with open(articles_js, "r", encoding="utf-8") as f:
            content = f.read()
        m = re.search(r'const ARTICLES = (\[[\s\S]*?\]);', content)
        if m:
            try:
                arts = json.loads(m.group(1))
                existing_slugs = {a["slug"] for a in arts}
            except Exception:
                pass

    published = set()
    for day, primary, *_ in PLAN:
        if make_slug(primary) in existing_slugs:
            published.add(day)
    return published


def week_of(day):
    return (day - 1) // ARTICLES_PER_WEEK + 1


def show_status():
    published = load_published()
    print(f"\n{'='*70}")
    print(f"  24-WEEK PLAN STATUS  ({len(published)}/{TOTAL_ARTICLES} articles published)")
    print(f"{'='*70}")
    for w in range(1, TOTAL_WEEKS + 1):
        week_days = [d for d in PLAN if week_of(d[0]) == w]
        done = sum(1 for d in week_days if d[0] in published)
        bar = "█" * done + "░" * (ARTICLES_PER_WEEK - done)
        print(f"\n  WEEK {w:02d}  [{bar}] {done}/{ARTICLES_PER_WEEK}")
        for day, primary, _, _, category in week_days:
            icon = "✅" if day in published else "⏳"
            tag = " [CORNERSTONE]" if day in CORNERSTONE_DAYS else ""
            print(f"    {icon} Day {day:02d} [{category[:14]:14}] {primary}{tag}")
    remaining = TOTAL_ARTICLES - len(published)
    weeks_left = remaining // ARTICLES_PER_WEEK
    print(f"\n  Done: {len(published)} | Remaining: {remaining} ({weeks_left} weeks left)")
    print(f"{'='*70}\n")


def run_day(day_num):
    # Keep the expensive publishing dependency behind the editorial pause so a
    # paused run cannot initialize a model client or write any content.
    from publisher_v2 import generate_article

    entry = next((d for d in PLAN if d[0] == day_num), None)
    if not entry:
        print(f"Day {day_num} not found.")
        return False
    day, primary, secondary, longtail, category = entry
    cornerstone = day in CORNERSTONE_DAYS
    print(f"\n{'='*70}")
    print(f"  DAY {day} | WEEK {week_of(day)} | {category}{' | CORNERSTONE' if cornerstone else ''}")
    print(f"  Topic: {primary}")
    print(f"{'='*70}\n")
    result = generate_article(primary, secondary, longtail, category, cornerstone=cornerstone)
    return bool(result)


def main():
    args = sys.argv[1:]

    if "--status" in args:
        show_status()
        return

    if PUBLISHING_PAUSED:
        print(
            "Publishing is paused for editorial review. "
            "New articles must be source-checked and human-reviewed before this plan resumes."
        )
        return

    if "--week" in args:
        idx = args.index("--week")
        w = int(args[idx + 1])
        week_days = [d for d in PLAN if week_of(d[0]) == w]
        print(f"\nWEEK {w} articles:")
        for day, primary, _, _, category in week_days:
            print(f"  Day {day:02d} [{category}] {primary}")
        return

    if "--day" in args:
        idx = args.index("--day")
        run_day(int(args[idx + 1]))
        return

    # Default: publish next unpublished day
    published = load_published()
    next_entry = next((d for d in PLAN if d[0] not in published), None)
    if not next_entry:
        print("All 72 articles published! 24-week plan complete.")
        show_status()
        return

    day_num = next_entry[0]
    print(f"Publishing Day {day_num} (Week {week_of(day_num)}): {next_entry[1]}")
    run_day(day_num)


if __name__ == "__main__":
    main()
