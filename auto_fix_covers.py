"""
auto_fix_covers.py — Post-publish safety net.

Scans all articles for:
  1. Pillow fallback covers (< 100 KB) → regenerates with DALL-E 3
  2. Missing section images → generates + injects into HTML

Run after batch_30days.py in the CCR agent, and locally whenever needed.
"""
import sys, os, io, time, requests, re
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR   = os.path.join(BASE_DIR, "images")
ARTICLES_DIR = os.path.join(BASE_DIR, "articles")
PILLOW_KB = 100  # covers below this size are Pillow fallbacks

REAL_PHOTO_RULES = (
    "CRITICAL RULES — strictly follow all of these: "
    "Frame the shot from the shoulders or collarbone UP only — never show the chest, bust, or body below the shoulders. Head-and-shoulders or face-and-hands-on-desk framing only. "
    "This must look like a real candid photo taken by a friend on a phone, NOT professional photography and NOT AI art. "
    "The person must look like a real ordinary human: slightly imperfect skin, natural pores, mild under-eye shadows, real hair texture with flyaways, no flawless symmetry. "
    "Clothing must be plain and ordinary: faded t-shirt, old hoodie, basic linen top — never stylish, never fitted, never flattering. "
    "Natural window light only — no studio lighting, no rim light, no beauty lighting, no glowing skin. "
    "Expression must be genuinely candid — slightly awkward, distracted, or absorbed — never a posed smile or model expression. "
    "Background must be messy or ordinary: cluttered desk, plain wall, basic kitchen — no magazine-style staging. "
    "No oversaturated colors, no HDR, no cinematic grading, no smooth AI skin, no perfect composition. "
    "If it looks like a stock photo or AI image, it is wrong. It must look like a real unedited snapshot."
)


def _openai_key():
    """Read OpenAI key fresh every call."""
    try:
        from config import OPENAI_API_KEY as key
    except Exception:
        key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        raise RuntimeError("OPENAI_API_KEY missing — cannot generate images")
    return key


def _openai_headers():
    return {
        "Authorization": f"Bearer {_openai_key()}",
        "Content-Type": "application/json",
    }


# ── ARTICLE-SPECIFIC PROMPTS (cover, [sec1, sec3, sec5]) ─────────────────
# Keyed by slug. Used before falling back to generic COVER_PROMPTS.
# Prompts describe scenes — no sensitive keywords that trigger content filters.
SLUG_PROMPTS = {
    "how-to-stay-calm-under-pressure": (
        "Candid lifestyle photo: a young woman, late 20s, at a tidy home desk with a laptop open, pausing from work and looking out the window with a calm, collected expression. Papers beside her. Soft afternoon light. Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos.",
        [
            "Candid photo: a young woman, early 30s, at a desk staring at a laptop screen with a tense, overwhelmed expression, jaw slightly tight. Afternoon light. Shot on 50mm f/2.0. Photorealistic candid lifestyle. No text, no logos.",
            "Lifestyle photo: a young woman, late 20s, leaning back slightly from her desk and looking out the window, hands resting on the armrests, composing herself before continuing. Warm window light. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
            "Candid photo: a young woman, mid-20s, closing her laptop at end of day with a calm, composed expression. A glass of water beside her. Warm late-afternoon light. Shot on 85mm f/1.8. Photorealistic lifestyle. No text, no logos.",
        ]
    ),
    "healthy-daily-habits": (
        "Candid lifestyle photo: a young woman, late 20s, in a bright kitchen making morning tea, calm and unhurried. She wears a soft cream top. Warm morning sunlight. Simple countertop. Shot on 85mm f/1.8, shallow depth of field. Photorealistic candid lifestyle. No text, no logos.",
        [
            "Candid photo: a young woman, early 30s, standing in a kitchen in early morning holding a mug of tea with both hands, still waking up, soft and unhurried. Warm morning light. Simple kitchen. Shot on 50mm f/2.0. Photorealistic candid lifestyle. No text, no logos.",
            "Lifestyle photo: a young woman, late 20s, eating a simple lunch at a kitchen table — bowl of salad and water glass. Relaxed, unhurried. Natural daylight. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
            "Candid photo: a young woman, mid-20s, sitting on a sofa in the evening writing in a journal by a small lamp, legs crossed, unhurried. Warm living room light. Shot on 85mm f/1.8. Photorealistic lifestyle. No text, no logos.",
        ]
    ),
    "signs-of-anxiety-disorder": (
        "Candid lifestyle photo: a young woman, late 20s, sitting on a sofa holding a mug of tea with both hands, looking out the window with a thoughtful and reflective expression. Soft living room light. Simple setting. Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos.",
        [
            "Candid photo: a young woman, early 30s, at a desk staring at her screen unfocused, one hand on her forehead, mind elsewhere. Soft afternoon light. Shot on 50mm f/2.0. Photorealistic candid lifestyle. No text, no logos.",
            "Lifestyle photo: a young woman, late 20s, sitting across a table from a friend, listening attentively with a thoughtful expression. Cafe setting, natural light. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
            "Candid photo: a young woman, mid-20s, writing in a journal at a kitchen table, calm and reflective. Morning light, a mug nearby. Shot on 85mm f/1.8. Photorealistic lifestyle. No text, no logos.",
        ]
    ),
    "how-to-focus-without-distractions": (
        "Candid lifestyle photo: a young woman, late 20s, at a clean minimal desk working on a laptop, deeply focused, earbuds in. Morning light from a window. Simple background. Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos.",
        [
            "Candid photo: a young woman, early 30s, at a desk glancing at her phone while a laptop is open, distracted expression. Afternoon light. Shot on 50mm f/2.0. Photorealistic candid. No text, no logos.",
            "Lifestyle photo: a young woman, late 20s, writing a to-do list in a notebook at her desk, phone face-down beside her. Focused and intentional. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
            "Candid photo: a young woman, mid-20s, working at a laptop with full concentration, slight forward lean, calm expression. Clean desk, warm light. Shot on 85mm f/1.8. Photorealistic lifestyle. No text, no logos.",
        ]
    ),
    "simple-morning-habits": (
        "Candid lifestyle photo: a young woman, late 20s, standing by a kitchen window holding a warm mug, looking outside in the early morning light. Soft golden tones, relaxed posture. Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos.",
        [
            "Candid photo: a young woman, early 30s, in a kitchen filling a glass of water at the sink in early morning, still waking up, quiet and slow. Warm morning light. Shot on 50mm f/2.0. Photorealistic candid lifestyle. No text, no logos.",
            "Lifestyle photo: a young woman, late 20s, making a simple breakfast — scrambled eggs on a plate, kettle in background. Warm kitchen light. Unhurried. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
            "Candid photo: a young woman, mid-20s, sitting at a kitchen table with a journal and mug, writing with a calm focused expression. Morning sunlight. Shot on 85mm f/1.8. Photorealistic lifestyle. No text, no logos.",
        ]
    ),
    "how-to-stop-panic-attacks": (
        "Candid lifestyle photo: a young woman, late 20s, sitting in a quiet corner of a room, eyes closed, one hand on her chest, breathing slowly and deliberately. Soft natural light. Calm and grounded. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
        [
            "Candid photo: a young woman, early 30s, sitting against a wall, knees pulled up slightly, catching her breath with a overwhelmed expression. Soft indoor light. Shot on 50mm f/2.0. Photorealistic candid. No text, no logos.",
            "Lifestyle photo: a young woman, late 20s, sitting cross-legged on a yoga mat doing slow deliberate breathing, eyes closed, hands open on knees. Natural light. Shot on 85mm f/1.8. Photorealistic wellness. No text, no logos.",
            "Candid photo: a young woman, mid-20s, sitting outside on a step, face turned up slightly to fresh air, calm relieved expression. Overcast daylight. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
        ]
    ),
    "how-to-stop-procrastination": (
        "Candid lifestyle photo: a young woman, late 20s, sitting down at her desk and opening her laptop with a determined, ready expression. Clean organized desk. Morning light. Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos.",
        [
            "Candid photo: a young woman, early 30s, sitting at a desk staring blankly at an open laptop, avoiding starting work, elbow on desk, chin resting on hand. Afternoon light. Shot on 50mm f/2.0. Photorealistic candid. No text, no logos.",
            "Lifestyle photo: a young woman, late 20s, writing a task list in a notebook with a pen, organized and intentional. Clean desk, morning light. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
            "Candid photo: a young woman, mid-20s, at her desk working through a checklist, pen in hand, focused and making progress. Warm afternoon light. Shot on 85mm f/1.8. Photorealistic lifestyle. No text, no logos.",
        ]
    ),
    "sleep-routine-tips": (
        "Candid lifestyle photo: a young woman, late 20s, in a soft robe sitting on the edge of her bed at night, lamp light glowing warm, winding down for sleep. Calm and relaxed. Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos.",
        [
            "Candid photo: a young woman, early 30s, lying in bed scrolling on her phone late at night, tired eyes, blue screen light. Dark room with a small lamp. Shot on 50mm f/2.0. Photorealistic candid. No text, no logos.",
            "Lifestyle photo: a young woman, late 20s, doing a gentle forward fold stretch beside her bed in the evening. Soft lamp light, tidy bedroom. Shot on 85mm f/1.8. Photorealistic candid wellness. No text, no logos.",
            "Candid photo: a young woman, mid-20s, asleep in a tidy bed, peaceful expression, soft morning light just starting. Cosy bedroom. Shot on 85mm f/1.8. Photorealistic lifestyle. No text, no logos.",
        ]
    ),
    "how-to-build-confidence": (
        "Candid lifestyle photo: a young woman, late 20s, standing in front of a mirror in a simple bedroom with a calm, steady expression — not smiling for the camera, just looking at herself with quiet assurance. Natural light. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
        [
            "Candid photo: a young woman, early 30s, sitting at a desk hesitating before clicking send on an email, uncertain expression. Soft indoor light. Shot on 50mm f/2.0. Photorealistic candid. No text, no logos.",
            "Lifestyle photo: a young woman, late 20s, speaking in a small group setting — gesturing with her hands, engaged and present. Natural indoor light. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
            "Candid photo: a young woman, mid-20s, walking on a footpath with upright posture and a relaxed, easy expression. Dappled daylight. Shot on 85mm f/1.8. Photorealistic lifestyle. No text, no logos.",
        ]
    ),
    "how-to-stay-motivated": (
        "Candid lifestyle photo: a young woman, late 20s, at her desk with a notebook open and a focused energized expression, pen in hand ready to work. Morning light. Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos.",
        [
            "Candid photo: a young woman, early 30s, sitting at her desk staring at her laptop looking flat and uninspired, chin in hand. Grey afternoon light. Shot on 50mm f/2.0. Photorealistic candid. No text, no logos.",
            "Lifestyle photo: a young woman, late 20s, reviewing a goal list in a notebook, circling something with a pen, focused and purposeful. Warm desk light. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
            "Candid photo: a young woman, mid-20s, working at her laptop with good posture and a pleased, productive expression. Clean desk, afternoon light. Shot on 85mm f/1.8. Photorealistic lifestyle. No text, no logos.",
        ]
    ),
    "healthy-lifestyle-tips": (
        "Candid lifestyle photo: a young woman, late 20s, in a bright kitchen slicing vegetables for a meal, relaxed and unhurried. Morning light, simple countertop. Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos.",
        [
            "Candid photo: a young woman, early 30s, in a supermarket aisle holding two food items and reading one label thoughtfully. Natural store light. Shot on 50mm f/2.0. Photorealistic candid. No text, no logos.",
            "Lifestyle photo: a young woman, late 20s, walking at a steady pace on a quiet residential footpath, relaxed expression. Overcast daylight. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
            "Candid photo: a young woman, mid-20s, doing a gentle yoga pose on a mat in her living room. Simple room, natural daylight. Shot on 85mm f/1.8. Photorealistic wellness lifestyle. No text, no logos.",
        ]
    ),
    "how-to-stop-worrying-about-the-future": (
        "Candid lifestyle photo: a young woman, late 20s, sitting by a window looking outside with a thoughtful, contemplative expression. Soft afternoon light. Simple room. Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos.",
        [
            "Candid photo: a young woman, early 30s, sitting at a table with a notepad, writing down a list of concerns, slightly furrowed brow. Soft indoor light. Shot on 50mm f/2.0. Photorealistic candid. No text, no logos.",
            "Lifestyle photo: a young woman, late 20s, sitting cross-legged on a yoga mat with eyes closed and a calm expression, meditating. Natural window light. Shot on 85mm f/1.8. Photorealistic wellness. No text, no logos.",
            "Candid photo: a young woman, mid-20s, sitting on a park bench looking ahead with a relaxed and present expression. Dappled daylight. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
        ]
    ),
    "time-management-tips": (
        "Candid lifestyle photo: a young woman, late 20s, at an organized desk with a planner open and a pen in hand, reviewing her schedule with a calm focused expression. Morning light. Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos.",
        [
            "Candid photo: a young woman, early 30s, at a cluttered desk with multiple tasks open, looking slightly overwhelmed, post-it notes around her laptop. Afternoon light. Shot on 50mm f/2.0. Photorealistic candid. No text, no logos.",
            "Lifestyle photo: a young woman, late 20s, blocking out her week in a planner with different coloured pens, organized and methodical. Clean desk, morning light. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
            "Candid photo: a young woman, mid-20s, closing her laptop at a reasonable hour with a satisfied, done-for-the-day expression. Warm late afternoon light. Shot on 85mm f/1.8. Photorealistic lifestyle. No text, no logos.",
        ]
    ),
    "daily-wellness-habits": (
        "Candid lifestyle photo: a young woman, late 20s, in a sunlit kitchen making morning tea, unhurried and calm. She wears a simple linen top. Warm morning light. Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos.",
        [
            "Candid photo: a young woman, early 30s, doing a simple morning stretch beside an open window. Natural light, simple bedroom. Shot on 50mm f/2.0. Photorealistic candid wellness. No text, no logos.",
            "Lifestyle photo: a young woman, late 20s, eating a balanced lunch at an outdoor table, relaxed and present. Natural daylight. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
            "Candid photo: a young woman, mid-20s, reading a paperback book on the sofa in the evening, soft lamp light. Cosy and unwinding. Shot on 85mm f/1.8. Photorealistic lifestyle. No text, no logos.",
        ]
    ),
    "deep-work-techniques": (
        "Candid lifestyle photo: a young woman, late 20s, in a deep state of focus at a clean desk — leaning slightly forward, eyes on laptop screen, noise-cancelling headphones on. Morning light. Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos.",
        [
            "Candid photo: a young woman, early 30s, at her desk glancing at buzzing phone notifications while trying to work, distracted expression. Afternoon light. Shot on 50mm f/2.0. Photorealistic candid. No text, no logos.",
            "Lifestyle photo: a young woman, late 20s, placing her phone face-down on the desk and putting on headphones, deliberate and intentional. Clean workspace. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
            "Candid photo: a young woman, mid-20s, leaning back and stretching after a long focused work session, relieved and accomplished expression. Warm afternoon light. Shot on 85mm f/1.8. Photorealistic lifestyle. No text, no logos.",
        ]
    ),
    "natural-energy-boosters": (
        "Candid lifestyle photo: a young woman, late 20s, stepping outside her front door in the early morning, arms slightly raised, eyes closed, face turned up to fresh air and sunlight. She wears a light jacket. Warm morning light. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
        [
            "Candid photo: a young woman, early 30s, sitting at her desk mid-morning looking tired, holding a coffee cup with heavy eyes. Natural office light. Shot on 50mm f/2.0. Photorealistic candid. No text, no logos.",
            "Lifestyle photo: a young woman, late 20s, at a kitchen counter filling a glass of water, a small bowl of fruit beside her. Bright morning light. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
            "Candid photo: a young woman, mid-20s, walking briskly on a residential pavement in the morning, earbuds in, light jacket. Overcast daylight. Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos.",
        ]
    ),
    "how-to-build-discipline": (
        "Candid lifestyle photo: a young woman, late 20s, sitting at her desk at the same time each morning, notebook open, mug beside her — clear daily routine visible. Consistent warm morning light. Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos.",
        [
            "Candid photo: a young woman, early 30s, alarm going off, looking at it with resistance, tempted to stay in bed. Dim morning bedroom light. Shot on 50mm f/2.0. Photorealistic candid. No text, no logos.",
            "Lifestyle photo: a young woman, late 20s, reviewing a habit tracker in a notebook, ticking off completed habits with a pen. Desk, morning light. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
            "Candid photo: a young woman, mid-20s, at her desk in a clear consistent work routine, calm and steady. Clean workspace, warm light. Shot on 85mm f/1.8. Photorealistic lifestyle. No text, no logos.",
        ]
    ),
    "daily-self-care-routine": (
        "Candid lifestyle photo: a young woman, late 20s, in a simple bathroom applying moisturiser in front of a mirror, calm morning routine. Natural bathroom light. She wears a soft robe. Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos.",
        [
            "Candid photo: a young woman, early 30s, rushing through a morning — grabbing keys and bag in a hurry, slightly stressed. Morning light. Shot on 50mm f/2.0. Photorealistic candid. No text, no logos.",
            "Lifestyle photo: a young woman, late 20s, sitting in a warm bath with eyes closed, calm and restorative. Soft bathroom light, no clutter. Shot on 85mm f/1.8. Photorealistic candid wellness. No text, no logos.",
            "Candid photo: a young woman, mid-20s, in her bedroom at night — journal open, lamp on, doing a calm evening wind-down routine. Cosy light. Shot on 85mm f/1.8. Photorealistic lifestyle. No text, no logos.",
        ]
    ),
    "how-to-reset-your-life": (
        "Candid lifestyle photo: a young woman, late 20s, sitting cross-legged on a clean floor surrounded by neatly sorted items, a fresh notebook open in her lap, looking forward with a calm determined expression. Natural light. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
        [
            "Candid photo: a young woman, early 30s, sitting at a messy overwhelmed desk, staring at it with a heavy expression. Flat afternoon light. Shot on 50mm f/2.0. Photorealistic candid. No text, no logos.",
            "Lifestyle photo: a young woman, late 20s, sorting through items and placing them in a box, decluttering her space. Natural light, simple room. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
            "Candid photo: a young woman, mid-20s, sitting at a newly clean and organized desk with a fresh notebook open, ready to start. Morning light. Shot on 85mm f/1.8. Photorealistic lifestyle. No text, no logos.",
        ]
    ),
    "productivity-system": (
        "Candid lifestyle photo: a young woman, late 20s, at an organized desk with a planner, colour-coded tabs, and a laptop — calm and clearly in command of her workflow. Morning light. Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos.",
        [
            "Candid photo: a young woman, early 30s, looking at three browser tabs open at once on her laptop, overwhelmed and unfocused. Afternoon light. Shot on 50mm f/2.0. Photorealistic candid. No text, no logos.",
            "Lifestyle photo: a young woman, late 20s, setting up a weekly system in a notebook — drawing columns and writing headings with a pen. Clean desk, morning light. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
            "Candid photo: a young woman, mid-20s, working methodically through her task list at a desk, crossing items off with focus. Warm afternoon light. Shot on 85mm f/1.8. Photorealistic lifestyle. No text, no logos.",
        ]
    ),
    "life-balance-habits": (
        "Candid lifestyle photo: a young woman, late 20s, sitting on a park bench in the middle of the day — shoes off, relaxed, eyes closed, face in the sun. Ordinary park, natural daylight. Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos.",
        [
            "Candid photo: a young woman, early 30s, getting home from work exhausted — dropping her bag by the door, shoulders heavy. Dim hallway light. Shot on 50mm f/2.0. Photorealistic candid. No text, no logos.",
            "Lifestyle photo: a young woman, late 20s, cooking a simple meal at home in the evening, phone away, relaxed and present. Warm kitchen light. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
            "Candid photo: a young woman, mid-20s, reading a book on the sofa on a weekend afternoon, completely at ease. Soft natural light. Shot on 85mm f/1.8. Photorealistic lifestyle. No text, no logos.",
        ]
    ),
    "how-to-change-your-mindset": (
        "Candid lifestyle photo: a young woman, late 20s, standing at a window looking out with a quiet, forward-looking expression — thoughtful and determined, not posed. Natural light. Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos.",
        [
            "Candid photo: a young woman, early 30s, sitting with her head slightly down, staring at nothing, a look of being stuck in repetitive thoughts. Dim indoor light. Shot on 50mm f/2.0. Photorealistic candid. No text, no logos.",
            "Lifestyle photo: a young woman, late 20s, writing in a journal at a table, pausing to think and then continuing to write — reframing something on the page. Warm desk light. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
            "Candid photo: a young woman, mid-20s, walking forward on a footpath with relaxed posture and an easy, light expression. Natural daylight. Shot on 85mm f/1.8. Photorealistic lifestyle. No text, no logos.",
        ]
    ),
    "habit-building-system": (
        "Candid lifestyle photo: a young woman, late 20s, at a desk marking a habit tracker in a notebook with a pen, small satisfied expression as she checks off another day. Morning light. Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos.",
        [
            "Candid photo: a young woman, early 30s, looking at a blank new notebook on her desk, unsure where to start, hesitant expression. Soft indoor light. Shot on 50mm f/2.0. Photorealistic candid. No text, no logos.",
            "Lifestyle photo: a young woman, late 20s, drawing up a simple habit tracker grid in a notebook, organized and methodical. Clean desk, morning light. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
            "Candid photo: a young woman, mid-20s, completing her morning routine — making tea, journal open beside her, consistent and unhurried. Warm morning light. Shot on 85mm f/1.8. Photorealistic lifestyle. No text, no logos.",
        ]
    ),
    "improve-daily-routine": (
        "Candid lifestyle photo: a young woman, late 20s, at a well-organized kitchen table — journal, mug, and planner laid out for a calm intentional morning. Soft morning light. Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos.",
        [
            "Candid photo: a young woman, early 30s, rushing chaotically through her morning — searching for keys, bag open, slightly frantic. Bright morning light. Shot on 50mm f/2.0. Photorealistic candid. No text, no logos.",
            "Lifestyle photo: a young woman, late 20s, sitting with a planner and a warm drink, thoughtfully planning her ideal day. Clean table, morning light. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
            "Candid photo: a young woman, mid-20s, moving through her morning routine calmly and in order — making tea, then sitting to write, unhurried. Warm morning light. Shot on 85mm f/1.8. Photorealistic lifestyle. No text, no logos.",
        ]
    ),
    "how-to-improve-your-life": (
        "Candid lifestyle photo: a young woman, late 20s, standing outside on a quiet street looking ahead with a calm, open expression — not posed, just present and forward-looking. Soft daylight. Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos.",
        [
            "Candid photo: a young woman, early 30s, sitting at her desk looking stuck and flat, staring at a blank screen with no energy. Grey afternoon light. Shot on 50mm f/2.0. Photorealistic candid. No text, no logos.",
            "Lifestyle photo: a young woman, late 20s, writing goals in a notebook at a table, circling the most important one, intentional. Morning light. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
            "Candid photo: a young woman, mid-20s, walking briskly and looking energized, carrying a reusable bag, early morning light. Residential street. Shot on 85mm f/1.8. Photorealistic lifestyle. No text, no logos.",
        ]
    ),
    "success-habits": (
        "Candid lifestyle photo: a young woman, late 20s, at her desk early in the morning — lamp on, notebook open, mug of tea, working before the day gets busy. Dim warm light. Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos.",
        [
            "Candid photo: a young woman, early 30s, lying in bed past her alarm, phone in hand, still scrolling — missing her morning routine. Dim bedroom. Shot on 50mm f/2.0. Photorealistic candid. No text, no logos.",
            "Lifestyle photo: a young woman, late 20s, reviewing her weekly goals notebook, ticking off completed tasks with focus. Clean desk, morning light. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
            "Candid photo: a young woman, mid-20s, finishing a piece of meaningful work at her desk and leaning back with a quiet satisfied expression. Warm afternoon light. Shot on 85mm f/1.8. Photorealistic lifestyle. No text, no logos.",
        ]
    ),
    "healthy-living-tips": (
        "Candid lifestyle photo: a young woman, late 20s, in a bright kitchen arranging fresh vegetables on a chopping board, relaxed and unhurried. Morning light. Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos.",
        [
            "Candid photo: a young woman, early 30s, at a petrol station convenience store looking tired, picking up a packaged snack — not her best choice. Flat indoor light. Shot on 50mm f/2.0. Photorealistic candid. No text, no logos.",
            "Lifestyle photo: a young woman, late 20s, jogging at an easy pace on a quiet residential path, light jacket, earbuds in. Overcast morning. Shot on 85mm f/1.8. Photorealistic candid. No text, no logos.",
            "Candid photo: a young woman, mid-20s, in bed at a reasonable hour, lamp off, peaceful and settled in for sleep. Soft dim light. Shot on 85mm f/1.8. Photorealistic lifestyle. No text, no logos.",
        ]
    ),
}

# ── GENERIC FALLBACK PROMPTS (by category) ────────────────────────────────
COVER_PROMPTS = {
    "Mental Wellness": (
        "Candid lifestyle photo: a young woman, late 20s, in a quiet home setting — "
        "bedroom, living room, or kitchen — in a calm intentional moment after managing stress. "
        "Natural body language, warm soft window light. Real skin, no perfection. "
        "Shot on 85mm f/1.8, shallow depth of field, warm tones. "
        "Photorealistic documentary wellness photography. No text, no logos, no watermarks."
    ),
    "Productivity": (
        "Candid lifestyle photo: a young woman, late 20s, at a clean minimal home desk, "
        "writing in a planner or looking at a laptop with calm focused expression. "
        "Natural window light, a plant nearby, warm neutral tones. Real skin. "
        "Shot on 85mm f/1.8, shallow depth of field. "
        "Photorealistic candid lifestyle photography. No text, no logos, no watermarks."
    ),
    "Healthy Lifestyle": (
        "Candid lifestyle photo: a young woman, late 20s, in a bright kitchen or nature setting, "
        "holding a warm mug or moving gently. Warm morning light, real skin, genuine expression. "
        "Shot on 85mm f/1.8, shallow depth of field, warm tones. "
        "Photorealistic candid wellness photography. No text, no logos, no watermarks."
    ),
}

SECTION_PROMPTS = {
    "Mental Wellness": [
        ("Candid photo: a young woman, early 30s, sitting on a sofa pressing one hand lightly "
         "to her chest, wide eyes showing early stress building. Real skin, natural light. "
         "Shot on 50mm f/2.0, warm tones. Photorealistic lifestyle. No text, no logos."),
        ("Candid photo: a young woman, late 20s, doing a breathing exercise — eyes closed, "
         "hands on knees, sitting cross-legged on a yoga mat. Soft natural light. "
         "Shot on 85mm f/1.8. Photorealistic wellness lifestyle. No text, no logos."),
        ("Morning lifestyle photo: a young woman, mid-20s, journaling at a kitchen table "
         "with a warm mug beside her. Calm focused expression, morning sunlight through window. "
         "Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos."),
    ],
    "Productivity": [
        ("Candid photo: a young woman, early 30s, at a desk staring at a laptop with a slightly "
         "overwhelmed expression. Real work stress, afternoon light. "
         "Shot on 50mm f/2.0. Photorealistic lifestyle. No text, no logos."),
        ("Candid photo: a young woman, late 20s, writing in a planner at a clean desk, "
         "calm and intentional. Morning light, plant nearby. "
         "Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos."),
        ("Lifestyle photo: a young woman, mid-20s, taking a break at her desk — arms stretched "
         "above her head, eyes closed, small relieved smile. Warm tones. "
         "Shot on 85mm f/1.8. Photorealistic candid. No text, no logos."),
    ],
    "Healthy Lifestyle": [
        ("Candid photo: a young woman, early 30s, preparing a healthy breakfast in a bright "
         "kitchen. Natural morning light, real skin, genuine moment. "
         "Shot on 50mm f/2.0. Photorealistic lifestyle. No text, no logos."),
        ("Lifestyle photo: a young woman, late 20s, walking on a quiet tree-lined path, "
         "calm and present. Dappled sunlight, warm tones. "
         "Shot on 85mm f/1.8. Photorealistic candid lifestyle. No text, no logos."),
        ("Morning lifestyle photo: a young woman, mid-20s, sitting at a kitchen table with "
         "a warm mug, eyes soft and present. Warm morning light. "
         "Shot on 85mm f/1.8. Photorealistic lifestyle. No text, no logos."),
    ],
}


def generate_image(prompt, filename, fmt, max_kb):
    """Generate image via DALL-E 3 (synchronous — no polling needed)."""
    full_prompt = f"{prompt} {REAL_PHOTO_RULES}"
    body = {
        "model": "dall-e-3",
        "prompt": full_prompt,
        "size": "1792x1024",
        "quality": "standard",
        "style": "natural",
        "n": 1,
    }
    try:
        r = requests.post(
            "https://api.openai.com/v1/images/generations",
            json=body, headers=_openai_headers(), timeout=120
        )
    except Exception as e:
        print(f"    Request error: {e}")
        return False
    if r.status_code != 200:
        print(f"    API error {r.status_code}: {r.text[:200]}")
        return False
    image_url = r.json()["data"][0]["url"]
    img_resp = requests.get(image_url, timeout=60)
    if img_resp.status_code != 200:
        return False
    img = Image.open(io.BytesIO(img_resp.content)).convert("RGB")
    img = img.resize((1920, 1080), Image.LANCZOS)
    out_path = os.path.join(IMAGES_DIR, filename)
    if fmt == "JPEG":
        for q in range(88, 15, -4):
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=q, optimize=True)
            if buf.tell() / 1024 <= max_kb:
                break
    else:
        for q in range(92, 10, -5):
            buf = io.BytesIO()
            img.save(buf, format="WEBP", quality=q, method=4)
            if buf.tell() / 1024 <= max_kb:
                break
    with open(out_path, "wb") as f:
        f.write(buf.getvalue())
    print(f"    Saved {filename} ({os.path.getsize(out_path)//1024}KB)")
    return True


def inject_sections(slug, html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    if f"{slug}-sec1.webp" in html:
        return  # already injected
    h2s = list(re.finditer(r'<h2>[^<]+</h2>', html))
    if len(h2s) < 6:
        print(f"    WARNING: only {len(h2s)} h2s — skipping injection")
        return
    img_style = 'style="width:100%;border-radius:10px;margin:28px 0 20px;display:block;object-fit:cover;" loading="lazy"'
    injections = [
        (h2s[1].start(), f"{slug}-sec1.webp", "lifestyle wellness photo section 1"),
        (h2s[3].start(), f"{slug}-sec3.webp", "lifestyle wellness photo section 3"),
        (h2s[5].start(), f"{slug}-sec5.webp", "lifestyle wellness photo section 5"),
    ]
    for pos, fname, alt in reversed(injections):
        tag = f'\n      <img src="../images/{fname}" alt="{alt}" {img_style}>\n\n      '
        html = html[:pos] + tag + html[pos:]
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"    Section images injected into HTML")


def get_category(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    for cat in ["Mental Wellness", "Productivity", "Healthy Lifestyle"]:
        if cat in content:
            return cat
    return "Mental Wellness"


def main():
    html_files = sorted(f for f in os.listdir(ARTICLES_DIR) if f.endswith(".html"))
    needs_fix = []

    for html_file in html_files:
        slug = html_file[:-5]
        cover = os.path.join(IMAGES_DIR, f"{slug}.jpg")
        sec1  = os.path.join(IMAGES_DIR, f"{slug}-sec1.webp")
        if not os.path.exists(cover):
            continue
        cover_kb  = os.path.getsize(cover) / 1024
        bad_cover = cover_kb < PILLOW_KB
        no_secs   = not os.path.exists(sec1)
        if bad_cover or no_secs:
            needs_fix.append((slug, html_file, bad_cover, no_secs, cover_kb))

    if not needs_fix:
        print("All articles OK — no Pillow fallbacks detected.")
        return

    print(f"\n{len(needs_fix)} article(s) need fixing:\n")
    fixed = 0
    for slug, html_file, bad_cover, no_secs, cover_kb in needs_fix:
        html_path = os.path.join(ARTICLES_DIR, html_file)
        category  = get_category(html_path)
        issues    = []
        if bad_cover: issues.append(f"Pillow cover ({cover_kb:.0f}KB)")
        if no_secs:   issues.append("missing section images")
        print(f"  {slug} — {', '.join(issues)}")

        ok = True
        img_count = 0  # track how many images we've generated this run

        # Use article-specific prompts when available, fall back to category defaults
        if slug in SLUG_PROMPTS:
            cover_prompt = SLUG_PROMPTS[slug][0]
            sec_prompts  = SLUG_PROMPTS[slug][1]
        else:
            cover_prompt = COVER_PROMPTS.get(category, COVER_PROMPTS["Mental Wellness"])
            sec_prompts  = SECTION_PROMPTS.get(category, SECTION_PROMPTS["Mental Wellness"])

        if bad_cover:
            if img_count > 0:
                print(f"    Waiting 65s (rate limit)...")
                time.sleep(65)
            if generate_image(cover_prompt, f"{slug}.jpg", "JPEG", 250):
                img_count += 1
            else:
                print(f"    Cover generation failed — skipping")
                ok = False

        if no_secs and ok:
            sec_ok = 0
            for i, prompt in enumerate(sec_prompts):
                idx = [1, 3, 5][i]
                if img_count > 0:
                    print(f"    Waiting 65s (rate limit)...")
                    time.sleep(65)
                if generate_image(prompt, f"{slug}-sec{idx}.webp", "WEBP", 500):
                    sec_ok += 1
                    img_count += 1
            if sec_ok == 3:
                inject_sections(slug, html_path)
            else:
                print(f"    Only {sec_ok}/3 section images generated")
                ok = False

        if ok:
            fixed += 1

    print(f"\nauto_fix_covers: {fixed}/{len(needs_fix)} articles fixed.")


if __name__ == "__main__":
    main()
