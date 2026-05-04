"""
NicheHubPro — 12-Week Strategic Publishing Plan
6 articles/week | 72 articles total | 12 weeks

Distribution: Mental Wellness 30% | Productivity 35% | Healthy Lifestyle 35%

Usage:
  python batch_12weeks.py             <- publish next unpublished day
  python batch_12weeks.py --day 5     <- publish specific day
  python batch_12weeks.py --status    <- show progress
  python batch_12weeks.py --week 3    <- show week 3 articles
"""

import sys, os, re, time, json
sys.stdout.reconfigure(encoding='utf-8')
from publisher_v2 import generate_article

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
TRACKING_FILE = os.path.join(BASE_DIR, "published_12weeks.txt")

# ── 12-WEEK PLAN ──────────────────────────────────────────────────────────────
# Format: (day, primary, secondary, longtail, category)
# 6 articles/week = days 1-72
# Publishing order per week: MW → MW → Prod → Prod → HL → HL

PLAN = [

    # ════════════════════════════════════════════════════════════════════════
    # WEEK 1 — Overthinking + Procrastination + Energy
    # ════════════════════════════════════════════════════════════════════════
    (1,  "how to stop overthinking everything",        "overthinking causes",               "why do I overthink every small decision",                   "Mental Wellness"),
    (2,  "signs of mental burnout and how to recover", "burnout recovery tips",             "how do I know if I have mental burnout",                    "Mental Wellness"),
    (3,  "how to stop procrastinating immediately",    "beat procrastination fast",         "why do I procrastinate even when I want to do things",      "Productivity"),
    (4,  "pomodoro technique explained for beginners", "pomodoro method productivity",      "how does the pomodoro technique work step by step",         "Productivity"),
    (5,  "why you feel tired all the time",            "constant fatigue causes",           "why am I always tired even after sleeping",                 "Healthy Lifestyle"),
    (6,  "best morning habits for more energy",        "morning energy routine",            "what morning habits give you the most energy",              "Healthy Lifestyle"),

    # ════════════════════════════════════════════════════════════════════════
    # WEEK 2 — Anxiety + Time + Sleep
    # ════════════════════════════════════════════════════════════════════════
    (7,  "how to reduce anxiety naturally",            "natural anxiety relief",            "how to reduce anxiety without medication",                  "Mental Wellness"),
    (8,  "emotional exhaustion vs burnout",            "emotional exhaustion symptoms",     "what is the difference between burnout and emotional exhaustion", "Mental Wellness"),
    (9,  "time blocking for beginners",                "time blocking schedule",            "how to use time blocking to be more productive",            "Productivity"),
    (10, "deep work vs multitasking",                  "single tasking benefits",           "why deep work is better than multitasking",                 "Productivity"),
    (11, "healthy sleep habits that improve energy",   "better sleep tips",                 "what sleep habits will give me more energy during the day", "Healthy Lifestyle"),
    (12, "best foods for focus and concentration",     "brain food for focus",              "what foods help you concentrate and focus better",          "Healthy Lifestyle"),

    # ════════════════════════════════════════════════════════════════════════
    # WEEK 3 — Motivation + Habits + Sleep-Mental Connection
    # ════════════════════════════════════════════════════════════════════════
    (13, "why you have no motivation anymore",         "lost motivation causes",            "why do I have no motivation to do anything anymore",        "Mental Wellness"),
    (14, "how to improve emotional resilience",        "emotional resilience tips",         "how to build emotional resilience after hard times",        "Mental Wellness"),
    (15, "how to build habits that actually stick",    "habit formation science",           "why do my habits never stick and how to fix it",            "Productivity"),
    (16, "best productivity systems explained",        "productivity frameworks",           "what is the best productivity system for daily life",       "Productivity"),
    (17, "how sleep affects mental health",            "sleep and mental health connection","how does poor sleep affect your mental health",             "Healthy Lifestyle"),
    (18, "healthy habits to start this week",          "simple healthy habits",             "what are the easiest healthy habits to start right now",    "Healthy Lifestyle"),

    # ════════════════════════════════════════════════════════════════════════
    # WEEK 4 — Negative Thinking + Time Management + Routine
    # ════════════════════════════════════════════════════════════════════════
    (19, "how to stop negative thinking patterns",     "break negative thought cycles",     "how to stop negative thinking patterns in your mind",       "Mental Wellness"),
    (20, "daily habits for better mental health",      "mental health habits",              "what daily habits improve mental health the most",          "Mental Wellness"),
    (21, "best time management techniques ranked",     "time management strategies",        "which time management techniques actually work",            "Productivity"),
    (22, "how to focus better at work",                "improve focus at work",             "how to focus better at work when you keep getting distracted", "Productivity"),
    (23, "morning routine for a healthy lifestyle",    "healthy morning routine",           "what should a healthy morning routine look like",           "Healthy Lifestyle"),
    (24, "how to improve energy naturally",            "natural energy boost tips",         "how to get more energy during the day without caffeine",    "Healthy Lifestyle"),

    # ════════════════════════════════════════════════════════════════════════
    # WEEK 5 — Overwhelm + Discipline + Nutrition
    # ════════════════════════════════════════════════════════════════════════
    (25, "how to calm down when overwhelmed",          "overwhelm relief techniques",       "what to do when you feel completely overwhelmed",           "Mental Wellness"),
    (26, "why you always feel stressed",               "chronic stress causes",             "why do I always feel stressed and anxious for no reason",   "Mental Wellness"),
    (27, "how to build self discipline",               "self discipline tips",              "how to build self discipline when you have none",           "Productivity"),
    (28, "why discipline beats motivation",            "discipline vs motivation",          "why discipline is more important than motivation",          "Productivity"),
    (29, "best healthy snacks for energy",             "energy boosting snacks",            "what are the best healthy snacks to eat for energy",       "Healthy Lifestyle"),
    (30, "daily stretching routine for beginners",     "simple stretching routine",         "what is a good daily stretching routine for beginners",    "Healthy Lifestyle"),

    # ════════════════════════════════════════════════════════════════════════
    # WEEK 6 — Burnout Recovery + Habits + Walking/Sleep
    # ════════════════════════════════════════════════════════════════════════
    (31, "how to recover from emotional burnout",      "burnout recovery steps",            "how long does it take to recover from emotional burnout",   "Mental Wellness"),
    (32, "how to stop catastrophic thinking",          "catastrophizing anxiety",           "how to stop catastrophic thinking and worst case scenarios","Mental Wellness"),
    (33, "best habit tracker methods that work",       "habit tracking systems",            "what is the best way to track habits daily",                "Productivity"),
    (34, "how to create a productive routine",         "productive daily schedule",         "how to create a daily routine that makes you productive",   "Productivity"),
    (35, "benefits of walking every day",              "daily walking health benefits",     "what happens to your body when you walk every day",        "Healthy Lifestyle"),
    (36, "best evening habits for better sleep",       "bedtime routine tips",              "what evening habits help you sleep better at night",       "Healthy Lifestyle"),

    # ════════════════════════════════════════════════════════════════════════
    # WEEK 7 — Work Stress + Focus + Exercise-Mental Link
    # ════════════════════════════════════════════════════════════════════════
    (37, "how to deal with stress at work",            "work stress management",            "how to deal with stress and anxiety at work",               "Mental Wellness"),
    (38, "why you feel mentally drained",              "mental fatigue causes",             "why do I feel mentally drained after doing nothing",        "Mental Wellness"),
    (39, "best focus techniques for students",         "study focus tips",                  "how to focus and study without getting distracted",         "Productivity"),
    (40, "how to avoid distractions while working",    "eliminate distractions tips",       "how to avoid distractions and stay focused while working",  "Productivity"),
    (41, "healthy daily routine checklist",            "daily routine for health",          "what should a healthy daily routine checklist include",     "Healthy Lifestyle"),
    (42, "how exercise improves mental health",        "exercise mental health benefits",   "how does exercise help with anxiety and depression",        "Healthy Lifestyle"),

    # ════════════════════════════════════════════════════════════════════════
    # WEEK 8 — Sleep-Anxiety + Productivity vs Motivation + Sleep Foods
    # NOTE: "How to Stop Overthinking at Night" replaced with fresh topic
    # ════════════════════════════════════════════════════════════════════════
    (43, "how to fall asleep when your mind won't stop","racing mind at night",             "how to fall asleep fast when you can't stop thinking",      "Mental Wellness"),
    (44, "why anxiety feels physical",                  "physical symptoms of anxiety",     "why does anxiety cause physical symptoms in your body",     "Mental Wellness"),
    (45, "focus vs motivation explained",               "focus and motivation difference",  "what is the difference between focus and motivation",       "Productivity"),
    (46, "how to stay productive every day",            "consistent productivity tips",     "how to be productive every day even when you don't feel like it", "Productivity"),
    (47, "best foods for better sleep",                 "sleep improving foods",            "what foods help you sleep better at night",                 "Healthy Lifestyle"),
    (48, "how to fix your sleep schedule",              "reset sleep schedule tips",        "how to fix a broken sleep schedule fast",                   "Healthy Lifestyle"),

    # ════════════════════════════════════════════════════════════════════════
    # WEEK 9 — Emotional Numbness + Gamification + Hydration
    # ════════════════════════════════════════════════════════════════════════
    (49, "why you feel emotionally numb",              "emotional numbness causes",         "why do I feel emotionally numb and disconnected",           "Mental Wellness"),
    (50, "how to build mental toughness",              "mental toughness tips",             "how to build mental toughness and resilience",              "Mental Wellness"),
    (51, "how to gamify your life for productivity",   "gamification productivity",         "how to use gamification to be more productive",             "Productivity"),
    (52, "best productivity apps in 2026",             "top productivity tools",            "what are the best productivity apps to use in 2026",        "Productivity"),
    (53, "healthy habits for busy people",             "habits for busy schedule",          "how to stay healthy when you are extremely busy",           "Healthy Lifestyle"),
    (54, "how to drink more water every day",          "daily water intake tips",           "how to drink more water when you always forget",            "Healthy Lifestyle"),

    # ════════════════════════════════════════════════════════════════════════
    # WEEK 10 — Self-Sabotage + Goal Tracking + Mobility
    # ════════════════════════════════════════════════════════════════════════
    (55, "how to stop self sabotaging",                "self sabotage patterns",            "why do I self sabotage when things are going well",         "Mental Wellness"),
    (56, "why you feel lost in life",                  "feeling lost and directionless",    "what to do when you feel lost and have no direction in life","Mental Wellness"),
    (57, "how to track progress toward goals",         "goal tracking methods",             "how to track your goals and measure real progress",         "Productivity"),
    (58, "why most people fail at building habits",    "habit failure reasons",             "why do habits fail and how to prevent it",                  "Productivity"),
    (59, "best daily mobility exercises",              "mobility routine for beginners",    "what are the best mobility exercises to do every day",      "Healthy Lifestyle"),
    (60, "healthy routine for working from home",      "work from home wellness tips",      "how to stay healthy and productive working from home",      "Healthy Lifestyle"),

    # ════════════════════════════════════════════════════════════════════════
    # WEEK 11 — Confidence + Concentration + Sustainable Habits
    # ════════════════════════════════════════════════════════════════════════
    (61, "how to build confidence through discipline", "confidence and discipline link",    "how to build real confidence through daily discipline",     "Mental Wellness"),
    (62, "how to reset your mindset",                  "mindset reset techniques",          "how to reset your mindset when you feel stuck",             "Mental Wellness"),
    (63, "best routine planner methods",               "daily planner strategies",          "what is the best way to plan your daily routine",           "Productivity"),
    (64, "how to improve concentration naturally",     "natural focus improvement",         "how to improve concentration and focus without medication", "Productivity"),
    (65, "healthy morning routine checklist",          "morning wellness checklist",        "what should be on a healthy morning routine checklist",     "Healthy Lifestyle"),
    (66, "how to create sustainable healthy habits",   "lasting healthy habits",            "how to create healthy habits that you actually keep",       "Healthy Lifestyle"),

    # ════════════════════════════════════════════════════════════════════════
    # WEEK 12 — Psychology + Systems + Long-Term Lifestyle
    # ════════════════════════════════════════════════════════════════════════
    (67, "the psychology of discipline",               "discipline psychology science",     "what does psychology say about building discipline",        "Mental Wellness"),
    (68, "why small habits create big results",        "compound habits effect",            "how do small daily habits lead to big life changes",        "Mental Wellness"),
    (69, "how to design the perfect daily routine",    "ideal daily schedule",              "how to design a daily routine that maximizes productivity", "Productivity"),
    (70, "best self improvement systems explained",    "self improvement frameworks",       "what are the best self improvement systems that work",      "Productivity"),
    (71, "healthy productivity habits for entrepreneurs","entrepreneur wellness habits",    "what healthy habits do successful entrepreneurs follow",    "Healthy Lifestyle"),
    (72, "how to build a better lifestyle long term",  "sustainable lifestyle change",      "how to build a better lifestyle that actually lasts",       "Healthy Lifestyle"),
]

TOTAL_ARTICLES = len(PLAN)
TOTAL_WEEKS    = 12
ARTICLES_PER_WEEK = 6


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
        slug = re.sub(r'[^a-z0-9]+', '-', primary.lower()).strip('-')[:60]
        if slug in existing_slugs:
            published.add(day)
    return published


def week_of(day):
    return (day - 1) // ARTICLES_PER_WEEK + 1


def show_status():
    published = load_published()
    print(f"\n{'='*70}")
    print(f"  12-WEEK PLAN STATUS  ({len(published)}/{TOTAL_ARTICLES} articles published)")
    print(f"{'='*70}")
    for w in range(1, TOTAL_WEEKS + 1):
        week_days = [d for d in PLAN if week_of(d[0]) == w]
        done = sum(1 for d in week_days if d[0] in published)
        bar = "█" * done + "░" * (ARTICLES_PER_WEEK - done)
        print(f"\n  WEEK {w:02d}  [{bar}] {done}/{ARTICLES_PER_WEEK}")
        for day, primary, _, _, category in week_days:
            icon = "✅" if day in published else "⏳"
            print(f"    {icon} Day {day:02d} [{category[:14]:14}] {primary}")
    remaining = TOTAL_ARTICLES - len(published)
    weeks_left = remaining // ARTICLES_PER_WEEK
    print(f"\n  Done: {len(published)} | Remaining: {remaining} ({weeks_left} weeks left)")
    print(f"{'='*70}\n")


def run_day(day_num):
    entry = next((d for d in PLAN if d[0] == day_num), None)
    if not entry:
        print(f"Day {day_num} not found.")
        return False
    day, primary, secondary, longtail, category = entry
    print(f"\n{'='*70}")
    print(f"  DAY {day} | WEEK {week_of(day)} | {category}")
    print(f"  Topic: {primary}")
    print(f"{'='*70}\n")
    result = generate_article(primary, secondary, longtail, category)
    return bool(result)


def main():
    args = sys.argv[1:]

    if "--status" in args:
        show_status()
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
        print("All 72 articles published! 12-week plan complete.")
        show_status()
        return

    day_num = next_entry[0]
    print(f"Publishing Day {day_num} (Week {week_of(day_num)}): {next_entry[1]}")
    run_day(day_num)


if __name__ == "__main__":
    main()
