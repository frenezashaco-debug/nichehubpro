"""
Inject two upgrades into all 66 existing article HTML files:
1. Ebook + App CTA box (before "Where to Go From Here")
2. "Keep Reading" related articles box (before FAQ section)

Run: python inject_upgrades.py
"""

import os, re

ARTICLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "articles")

# ── FREE RESOURCES CTA ────────────────────────────────────────────────────
CTA_HTML = """
      <!-- FREE RESOURCES CTA -->
      <div style="background:var(--dark);border-radius:16px;padding:28px;margin:40px 0;display:flex;gap:20px;flex-wrap:wrap;align-items:center;justify-content:space-between;">
        <div style="flex:1;min-width:200px;">
          <span style="font-size:0.68rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#00E676;">Free Resources</span>
          <h3 style="color:#fff;font-size:1.1rem;font-weight:800;margin:8px 0 6px;line-height:1.3;">Put this into practice today.</h3>
          <p style="color:rgba(255,255,255,0.5);font-size:0.82rem;line-height:1.65;margin:0;">Our free ebook and habit tracker app were built to help you apply what you just read. No cost, no signup required.</p>
        </div>
        <div style="display:flex;flex-direction:column;gap:10px;min-width:210px;">
          <a href="/ebook/" style="display:flex;align-items:center;gap:10px;background:rgba(0,230,118,0.1);border:1px solid rgba(0,230,118,0.2);border-radius:10px;padding:10px 14px;text-decoration:none;transition:background 0.2s;" onmouseover="this.style.background='rgba(0,230,118,0.18)'" onmouseout="this.style.background='rgba(0,230,118,0.1)'">
            <span style="font-size:1.4rem;">📖</span>
            <div>
              <div style="font-size:0.78rem;font-weight:700;color:#00E676;">Free Ebook</div>
              <div style="font-size:0.72rem;color:rgba(255,255,255,0.45);">30-Day Discipline Reset</div>
            </div>
          </a>
          <a href="https://play.google.com/store/apps/details?id=com.ideafuel.idea_fuel" target="_blank" rel="noopener noreferrer" style="display:flex;align-items:center;gap:10px;background:rgba(107,175,146,0.1);border:1px solid rgba(107,175,146,0.2);border-radius:10px;padding:10px 14px;text-decoration:none;transition:background 0.2s;" onmouseover="this.style.background='rgba(107,175,146,0.18)'" onmouseout="this.style.background='rgba(107,175,146,0.1)'">
            <span style="font-size:1.4rem;">⚡</span>
            <div>
              <div style="font-size:0.78rem;font-weight:700;color:var(--green);">Free Android App</div>
              <div style="font-size:0.72rem;color:rgba(255,255,255,0.45);">IdeaFuel: Habit &amp; Focus Timer</div>
            </div>
          </a>
        </div>
      </div>

"""

# ── INTERNAL LINK MESH ────────────────────────────────────────────────────
# Each slug → list of (anchor_text, target_slug)
RELATED = {
    "anxiety-before-sleep":                [("how to calm anxiety quickly","/articles/how-to-calm-anxiety-quickly.html"),("how to stop overthinking at night","/articles/how-to-stop-overthinking-at-night.html"),("how to sleep better naturally","/articles/how-to-sleep-better-naturally.html"),("sleep routine tips","/articles/sleep-routine-tips.html")],
    "benefits-of-walking-daily":           [("how to increase energy naturally","/articles/how-to-increase-energy-naturally.html"),("healthy daily habits","/articles/healthy-daily-habits.html"),("natural energy boosters","/articles/natural-energy-boosters.html"),("how to reduce stress naturally","/articles/how-to-reduce-stress-naturally.html")],
    "best-foods-for-focus-and-concentration":[("how to improve mental clarity","/articles/how-to-improve-mental-clarity.html"),("natural energy boosters","/articles/natural-energy-boosters.html"),("how to focus without distractions","/articles/how-to-focus-without-distractions.html"),("deep work techniques","/articles/deep-work-techniques.html")],
    "best-morning-habits-for-more-energy": [("morning routine for mental health","/articles/morning-routine-for-mental-health.html"),("simple morning habits","/articles/simple-morning-habits.html"),("how to wake up early and feel good","/articles/how-to-increase-energy-naturally.html"),("natural energy boosters","/articles/natural-energy-boosters.html")],
    "daily-self-care-routine":             [("daily wellness habits","/articles/daily-wellness-habits.html"),("healthy daily habits","/articles/healthy-daily-habits.html"),("morning routine for mental health","/articles/morning-routine-for-mental-health.html"),("how to reset your life","/articles/how-to-reset-your-life.html")],
    "daily-wellness-habits":               [("daily self-care routine","/articles/daily-self-care-routine.html"),("healthy daily habits","/articles/healthy-daily-habits.html"),("simple morning habits","/articles/simple-morning-habits.html"),("life balance habits","/articles/life-balance-habits.html")],
    "deep-work-techniques":                [("how to focus without distractions","/articles/how-to-focus-without-distractions.html"),("time blocking for beginners","/articles/time-blocking-for-beginners.html"),("how to stop procrastination","/articles/how-to-stop-procrastination.html"),("productivity system","/articles/productivity-system.html")],
    "deep-work-vs-multitasking":           [("deep work techniques","/articles/deep-work-techniques.html"),("how to focus without distractions","/articles/how-to-focus-without-distractions.html"),("how to build discipline","/articles/how-to-build-discipline.html"),("time blocking for beginners","/articles/time-blocking-for-beginners.html")],
    "emotional-burnout-recovery":          [("signs of mental exhaustion","/articles/signs-of-mental-exhaustion.html"),("emotional exhaustion vs burnout","/articles/emotional-exhaustion-vs-burnout.html"),("how to reset your life","/articles/how-to-reset-your-life.html"),("how to detox your mind","/articles/how-to-detox-your-mind.html")],
    "emotional-exhaustion-vs-burnout":     [("signs of mental exhaustion","/articles/signs-of-mental-exhaustion.html"),("emotional burnout recovery","/articles/emotional-burnout-recovery.html"),("how to feel happy again","/articles/how-to-feel-happy-again.html"),("how to reduce stress naturally","/articles/how-to-reduce-stress-naturally.html")],
    "fear-of-failure-anxiety":             [("how to build confidence","/articles/how-to-build-confidence.html"),("how to stop worrying","/articles/how-to-stop-worrying.html"),("signs of anxiety disorder","/articles/signs-of-anxiety-disorder.html"),("how to stop negative thoughts","/articles/how-to-stop-negative-thoughts.html")],
    "foods-that-reduce-anxiety":           [("how to reduce anxiety naturally","/articles/how-to-reduce-anxiety-naturally.html"),("how to sleep better naturally","/articles/how-to-sleep-better-naturally.html"),("how to increase energy naturally","/articles/how-to-increase-energy-naturally.html"),("natural energy boosters","/articles/natural-energy-boosters.html")],
    "habit-building-system":               [("how to build discipline","/articles/how-to-build-discipline.html"),("how to stop procrastination","/articles/how-to-stop-procrastination.html"),("productivity system","/articles/productivity-system.html"),("how to stay motivated","/articles/how-to-stay-motivated.html")],
    "healthy-daily-habits":                [("daily wellness habits","/articles/daily-wellness-habits.html"),("daily self-care routine","/articles/daily-self-care-routine.html"),("simple morning habits","/articles/simple-morning-habits.html"),("healthy lifestyle tips","/articles/healthy-lifestyle-tips.html")],
    "healthy-lifestyle-tips":              [("healthy daily habits","/articles/healthy-daily-habits.html"),("healthy living tips","/articles/healthy-living-tips.html"),("daily wellness habits","/articles/daily-wellness-habits.html"),("benefits of walking daily","/articles/benefits-of-walking-daily.html")],
    "healthy-living-tips":                 [("healthy lifestyle tips","/articles/healthy-lifestyle-tips.html"),("healthy daily habits","/articles/healthy-daily-habits.html"),("natural energy boosters","/articles/natural-energy-boosters.html"),("how to improve your life","/articles/how-to-improve-your-life.html")],
    "healthy-sleep-habits-that-improve-energy":[("how to sleep better naturally","/articles/how-to-sleep-better-naturally.html"),("sleep routine tips","/articles/sleep-routine-tips.html"),("anxiety before sleep","/articles/anxiety-before-sleep.html"),("natural energy boosters","/articles/natural-energy-boosters.html")],
    "how-to-break-negative-thinking":      [("how to stop negative thoughts","/articles/how-to-stop-negative-thoughts.html"),("how to control your thoughts","/articles/how-to-control-your-thoughts.html"),("how to change your mindset","/articles/how-to-change-your-mindset.html"),("how to improve mental clarity","/articles/how-to-improve-mental-clarity.html")],
    "how-to-build-confidence":             [("how to stop negative thoughts","/articles/how-to-stop-negative-thoughts.html"),("fear of failure anxiety","/articles/fear-of-failure-anxiety.html"),("how to build discipline","/articles/how-to-build-discipline.html"),("how to change your mindset","/articles/how-to-change-your-mindset.html")],
    "how-to-build-discipline":             [("habit building system","/articles/habit-building-system.html"),("how to stop procrastination","/articles/how-to-stop-procrastination.html"),("how to stay motivated","/articles/how-to-stay-motivated.html"),("success habits","/articles/success-habits.html")],
    "how-to-calm-anxiety-quickly":         [("how to stop anxiety attacks","/articles/how-to-stop-anxiety-attacks.html"),("how to stop panic attacks","/articles/how-to-stop-panic-attacks.html"),("how to feel calm instantly","/articles/how-to-feel-calm-instantly.html"),("how to deal with anxiety daily","/articles/how-to-deal-with-anxiety-daily.html")],
    "how-to-calm-your-mind-instantly":     [("how to relax your mind","/articles/how-to-relax-your-mind.html"),("how to feel calm instantly","/articles/how-to-feel-calm-instantly.html"),("how to stop overthinking","/articles/how-to-stop-overthinking.html"),("how to detox your mind","/articles/how-to-detox-your-mind.html")],
    "how-to-change-your-mindset":          [("how to break negative thinking","/articles/how-to-break-negative-thinking.html"),("how to build confidence","/articles/how-to-build-confidence.html"),("how to improve your life","/articles/how-to-improve-your-life.html"),("how to reset your life","/articles/how-to-reset-your-life.html")],
    "how-to-control-your-thoughts":        [("how to stop overthinking","/articles/how-to-stop-overthinking.html"),("how to stop negative thoughts","/articles/how-to-stop-negative-thoughts.html"),("how to break negative thinking","/articles/how-to-break-negative-thinking.html"),("how to feel in control of your mind","/articles/how-to-feel-in-control-of-your-mind.html")],
    "how-to-deal-with-anxiety-daily":      [("how to calm anxiety quickly","/articles/how-to-calm-anxiety-quickly.html"),("how to reduce anxiety naturally","/articles/how-to-reduce-anxiety-naturally.html"),("signs of anxiety disorder","/articles/signs-of-anxiety-disorder.html"),("how to stop worrying","/articles/how-to-stop-worrying.html")],
    "how-to-detox-your-mind":              [("how to calm your mind instantly","/articles/how-to-calm-your-mind-instantly.html"),("how to relax your mind","/articles/how-to-relax-your-mind.html"),("how to reset your life","/articles/how-to-reset-your-life.html"),("how to feel happy again","/articles/how-to-feel-happy-again.html")],
    "how-to-feel-calm-instantly":          [("how to calm anxiety quickly","/articles/how-to-calm-anxiety-quickly.html"),("how to relax your mind","/articles/how-to-relax-your-mind.html"),("how to stop panic attacks","/articles/how-to-stop-panic-attacks.html"),("how to calm your mind instantly","/articles/how-to-calm-your-mind-instantly.html")],
    "how-to-feel-happy-again":             [("how to reset your life","/articles/how-to-reset-your-life.html"),("emotional burnout recovery","/articles/emotional-burnout-recovery.html"),("how to change your mindset","/articles/how-to-change-your-mindset.html"),("how to improve your life","/articles/how-to-improve-your-life.html")],
    "how-to-feel-in-control-of-your-mind": [("how to control your thoughts","/articles/how-to-control-your-thoughts.html"),("how to stop overthinking","/articles/how-to-stop-overthinking.html"),("how to build discipline","/articles/how-to-build-discipline.html"),("how to improve mental clarity","/articles/how-to-improve-mental-clarity.html")],
    "how-to-focus-without-distractions":   [("deep work techniques","/articles/deep-work-techniques.html"),("time blocking for beginners","/articles/time-blocking-for-beginners.html"),("how to stop procrastination","/articles/how-to-stop-procrastination.html"),("how to improve mental clarity","/articles/how-to-improve-mental-clarity.html")],
    "how-to-improve-mental-clarity":       [("how to focus without distractions","/articles/how-to-focus-without-distractions.html"),("how to increase energy naturally","/articles/how-to-increase-energy-naturally.html"),("deep work techniques","/articles/deep-work-techniques.html"),("why you feel tired all the time","/articles/why-you-feel-tired-all-the-time.html")],
    "how-to-improve-your-life":            [("how to reset your life","/articles/how-to-reset-your-life.html"),("how to change your mindset","/articles/how-to-change-your-mindset.html"),("success habits","/articles/success-habits.html"),("how to build discipline","/articles/how-to-build-discipline.html")],
    "how-to-increase-energy-naturally":    [("natural energy boosters","/articles/natural-energy-boosters.html"),("why you feel tired all the time","/articles/why-you-feel-tired-all-the-time.html"),("how to sleep better naturally","/articles/how-to-sleep-better-naturally.html"),("best morning habits for more energy","/articles/best-morning-habits-for-more-energy.html")],
    "how-to-reduce-anxiety-naturally":     [("how to calm anxiety quickly","/articles/how-to-calm-anxiety-quickly.html"),("foods that reduce anxiety","/articles/foods-that-reduce-anxiety.html"),("how to deal with anxiety daily","/articles/how-to-deal-with-anxiety-daily.html"),("how to reduce stress naturally","/articles/how-to-reduce-stress-naturally.html")],
    "how-to-reduce-stress-naturally":      [("how to relax your mind","/articles/how-to-relax-your-mind.html"),("how to reduce anxiety naturally","/articles/how-to-reduce-anxiety-naturally.html"),("healthy daily habits","/articles/healthy-daily-habits.html"),("benefits of walking daily","/articles/benefits-of-walking-daily.html")],
    "how-to-relax-your-mind":              [("how to calm your mind instantly","/articles/how-to-calm-your-mind-instantly.html"),("how to reduce stress naturally","/articles/how-to-reduce-stress-naturally.html"),("how to detox your mind","/articles/how-to-detox-your-mind.html"),("how to feel calm instantly","/articles/how-to-feel-calm-instantly.html")],
    "how-to-reset-your-life":              [("how to change your mindset","/articles/how-to-change-your-mindset.html"),("how to improve your life","/articles/how-to-improve-your-life.html"),("emotional burnout recovery","/articles/emotional-burnout-recovery.html"),("how to feel happy again","/articles/how-to-feel-happy-again.html")],
    "how-to-sleep-better-naturally":       [("anxiety before sleep","/articles/anxiety-before-sleep.html"),("sleep routine tips","/articles/sleep-routine-tips.html"),("healthy sleep habits that improve energy","/articles/healthy-sleep-habits-that-improve-energy.html"),("how to stop overthinking at night","/articles/how-to-stop-overthinking-at-night.html")],
    "how-to-stay-calm-under-pressure":     [("how to manage stress at work","/articles/how-to-deal-with-anxiety-daily.html"),("how to stop anxiety attacks","/articles/how-to-stop-anxiety-attacks.html"),("how to feel in control of your mind","/articles/how-to-feel-in-control-of-your-mind.html"),("how to build discipline","/articles/how-to-build-discipline.html")],
    "how-to-stay-motivated":               [("how to build discipline","/articles/how-to-build-discipline.html"),("habit building system","/articles/habit-building-system.html"),("how to stop procrastination","/articles/how-to-stop-procrastination.html"),("success habits","/articles/success-habits.html")],
    "how-to-stop-anxiety-attacks":         [("how to stop panic attacks","/articles/how-to-stop-panic-attacks.html"),("how to calm anxiety quickly","/articles/how-to-calm-anxiety-quickly.html"),("signs of anxiety disorder","/articles/signs-of-anxiety-disorder.html"),("how to deal with anxiety daily","/articles/how-to-deal-with-anxiety-daily.html")],
    "how-to-stop-negative-thoughts":       [("how to break negative thinking","/articles/how-to-break-negative-thinking.html"),("how to control your thoughts","/articles/how-to-control-your-thoughts.html"),("how to stop overthinking","/articles/how-to-stop-overthinking.html"),("how to change your mindset","/articles/how-to-change-your-mindset.html")],
    "how-to-stop-overthinking":            [("how to control your thoughts","/articles/how-to-control-your-thoughts.html"),("how to stop negative thoughts","/articles/how-to-stop-negative-thoughts.html"),("how to stop overthinking at night","/articles/how-to-stop-overthinking-at-night.html"),("how to feel in control of your mind","/articles/how-to-feel-in-control-of-your-mind.html")],
    "how-to-stop-overthinking-at-night":   [("anxiety before sleep","/articles/anxiety-before-sleep.html"),("how to sleep better naturally","/articles/how-to-sleep-better-naturally.html"),("how to stop overthinking","/articles/how-to-stop-overthinking.html"),("how to calm your mind instantly","/articles/how-to-calm-your-mind-instantly.html")],
    "how-to-stop-overthinking-at-work":    [("how to focus without distractions","/articles/how-to-focus-without-distractions.html"),("how to stop overthinking","/articles/how-to-stop-overthinking.html"),("how to stay calm under pressure","/articles/how-to-stay-calm-under-pressure.html"),("deep work techniques","/articles/deep-work-techniques.html")],
    "how-to-stop-overthinking-everything": [("how to stop overthinking","/articles/how-to-stop-overthinking.html"),("how to control your thoughts","/articles/how-to-control-your-thoughts.html"),("how to stop worrying","/articles/how-to-stop-worrying.html"),("how to feel in control of your mind","/articles/how-to-feel-in-control-of-your-mind.html")],
    "how-to-stop-panic-attacks":           [("how to stop anxiety attacks","/articles/how-to-stop-anxiety-attacks.html"),("how to calm anxiety quickly","/articles/how-to-calm-anxiety-quickly.html"),("how to feel calm instantly","/articles/how-to-feel-calm-instantly.html"),("signs of anxiety disorder","/articles/signs-of-anxiety-disorder.html")],
    "how-to-stop-procrastinating-immediately":[("how to stop procrastination","/articles/how-to-stop-procrastination.html"),("how to build discipline","/articles/how-to-build-discipline.html"),("how to focus without distractions","/articles/how-to-focus-without-distractions.html"),("habit building system","/articles/habit-building-system.html")],
    "how-to-stop-procrastination":         [("how to build discipline","/articles/how-to-build-discipline.html"),("habit building system","/articles/habit-building-system.html"),("how to focus without distractions","/articles/how-to-focus-without-distractions.html"),("how to stay motivated","/articles/how-to-stay-motivated.html")],
    "how-to-stop-worrying":                [("how to stop worrying about the future","/articles/how-to-stop-worrying-about-the-future.html"),("how to control your thoughts","/articles/how-to-control-your-thoughts.html"),("how to calm anxiety quickly","/articles/how-to-calm-anxiety-quickly.html"),("how to stop overthinking","/articles/how-to-stop-overthinking.html")],
    "how-to-stop-worrying-about-the-future":[("how to stop worrying","/articles/how-to-stop-worrying.html"),("how to stop overthinking","/articles/how-to-stop-overthinking.html"),("how to deal with anxiety daily","/articles/how-to-deal-with-anxiety-daily.html"),("how to change your mindset","/articles/how-to-change-your-mindset.html")],
    "improve-daily-routine":               [("daily wellness habits","/articles/daily-wellness-habits.html"),("productivity system","/articles/productivity-system.html"),("simple morning habits","/articles/simple-morning-habits.html"),("habit building system","/articles/habit-building-system.html")],
    "life-balance-habits":                 [("daily wellness habits","/articles/daily-wellness-habits.html"),("daily self-care routine","/articles/daily-self-care-routine.html"),("how to reset your life","/articles/how-to-reset-your-life.html"),("productivity system","/articles/productivity-system.html")],
    "morning-routine-for-mental-health":   [("simple morning habits","/articles/simple-morning-habits.html"),("best morning habits for more energy","/articles/best-morning-habits-for-more-energy.html"),("how to sleep better naturally","/articles/how-to-sleep-better-naturally.html"),("daily wellness habits","/articles/daily-wellness-habits.html")],
    "natural-energy-boosters":             [("how to increase energy naturally","/articles/how-to-increase-energy-naturally.html"),("why you feel tired all the time","/articles/why-you-feel-tired-all-the-time.html"),("how to sleep better naturally","/articles/how-to-sleep-better-naturally.html"),("healthy daily habits","/articles/healthy-daily-habits.html")],
    "pomodoro-technique-explained-for-beginners":[("time blocking for beginners","/articles/time-blocking-for-beginners.html"),("how to focus without distractions","/articles/how-to-focus-without-distractions.html"),("deep work techniques","/articles/deep-work-techniques.html"),("how to stop procrastination","/articles/how-to-stop-procrastination.html")],
    "productivity-system":                 [("habit building system","/articles/habit-building-system.html"),("time management tips","/articles/time-management-tips.html"),("how to build discipline","/articles/how-to-build-discipline.html"),("deep work techniques","/articles/deep-work-techniques.html")],
    "signs-of-anxiety-disorder":           [("how to deal with anxiety daily","/articles/how-to-deal-with-anxiety-daily.html"),("how to stop anxiety attacks","/articles/how-to-stop-anxiety-attacks.html"),("signs of mental exhaustion","/articles/signs-of-mental-exhaustion.html"),("how to reduce anxiety naturally","/articles/how-to-reduce-anxiety-naturally.html")],
    "signs-of-mental-burnout-and-how-to-recover":[("emotional burnout recovery","/articles/emotional-burnout-recovery.html"),("signs of mental exhaustion","/articles/signs-of-mental-exhaustion.html"),("emotional exhaustion vs burnout","/articles/emotional-exhaustion-vs-burnout.html"),("how to reset your life","/articles/how-to-reset-your-life.html")],
    "signs-of-mental-exhaustion":          [("emotional burnout recovery","/articles/emotional-burnout-recovery.html"),("emotional exhaustion vs burnout","/articles/emotional-exhaustion-vs-burnout.html"),("why you feel tired all the time","/articles/why-you-feel-tired-all-the-time.html"),("how to deal with anxiety daily","/articles/how-to-deal-with-anxiety-daily.html")],
    "simple-morning-habits":               [("morning routine for mental health","/articles/morning-routine-for-mental-health.html"),("best morning habits for more energy","/articles/best-morning-habits-for-more-energy.html"),("daily wellness habits","/articles/daily-wellness-habits.html"),("how to increase energy naturally","/articles/how-to-increase-energy-naturally.html")],
    "sleep-routine-tips":                  [("how to sleep better naturally","/articles/how-to-sleep-better-naturally.html"),("anxiety before sleep","/articles/anxiety-before-sleep.html"),("how to stop overthinking at night","/articles/how-to-stop-overthinking-at-night.html"),("healthy sleep habits that improve energy","/articles/healthy-sleep-habits-that-improve-energy.html")],
    "success-habits":                      [("habit building system","/articles/habit-building-system.html"),("how to build discipline","/articles/how-to-build-discipline.html"),("how to improve your life","/articles/how-to-improve-your-life.html"),("productivity system","/articles/productivity-system.html")],
    "time-blocking-for-beginners":         [("time management tips","/articles/time-management-tips.html"),("pomodoro technique explained for beginners","/articles/pomodoro-technique-explained-for-beginners.html"),("how to focus without distractions","/articles/how-to-focus-without-distractions.html"),("productivity system","/articles/productivity-system.html")],
    "time-management-tips":                [("time blocking for beginners","/articles/time-blocking-for-beginners.html"),("productivity system","/articles/productivity-system.html"),("how to stop procrastination","/articles/how-to-stop-procrastination.html"),("deep work techniques","/articles/deep-work-techniques.html")],
    "why-you-feel-tired-all-the-time":     [("how to increase energy naturally","/articles/how-to-increase-energy-naturally.html"),("natural energy boosters","/articles/natural-energy-boosters.html"),("signs of mental exhaustion","/articles/signs-of-mental-exhaustion.html"),("how to sleep better naturally","/articles/how-to-sleep-better-naturally.html")],
}


def build_keep_reading_html(slug):
    links = RELATED.get(slug, [])
    if not links:
        return ""
    items = "\n".join(
        f'          <li><a href="{url}" style="font-size:0.88rem;font-weight:500;color:var(--dark);text-decoration:none;line-height:1.5;">'
        f'→ {anchor}</a></li>'
        for anchor, url in links[:4]
    )
    return f"""
      <!-- KEEP READING -->
      <div style="background:var(--green-pale);border:1px solid var(--border);border-radius:12px;padding:20px 24px;margin:36px 0;">
        <p style="font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:var(--gray);margin-bottom:12px;">Keep Reading</p>
        <ul style="list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:10px;">
{items}
        </ul>
      </div>

"""


def inject_file(filepath):
    slug = os.path.basename(filepath).replace(".html", "")
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    changed = False

    # 1. Inject CTA before "Where to Go From Here" (skip if already injected)
    if "FREE RESOURCES CTA" not in html and "<h2>Where to Go From Here</h2>" in html:
        html = html.replace("<h2>Where to Go From Here</h2>", CTA_HTML + "      <h2>Where to Go From Here</h2>", 1)
        changed = True

    # 2. Inject Keep Reading before FAQ section (skip if already injected)
    keep_reading = build_keep_reading_html(slug)
    if keep_reading and "KEEP READING" not in html and '<div class="faq-section">' in html:
        html = html.replace('<div class="faq-section">', keep_reading + '      <div class="faq-section">', 1)
        changed = True

    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        return True
    return False


def main():
    files = sorted(f for f in os.listdir(ARTICLES_DIR) if f.endswith(".html"))
    updated = 0
    for fname in files:
        filepath = os.path.join(ARTICLES_DIR, fname)
        if inject_file(filepath):
            updated += 1
            print(f"  Updated: {fname}")
        else:
            print(f"  Skipped: {fname}")
    print(f"\nDone. {updated}/{len(files)} articles updated.")


if __name__ == "__main__":
    main()
