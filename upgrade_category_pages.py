"""
Upgrade all 4 category pages with:
- Sort bar (Newest / Oldest / A-Z)
- Article count badge in header
- Resources CTA banner at bottom of article grid
"""

import os, re

BASE = os.path.dirname(os.path.abspath(__file__))

PAGES = {
    "mental-wellness/index.html": {
        "filter": "a.cat_slug === 'mental-wellness'",
        "label": "Mental Wellness",
    },
    "productivity/index.html": {
        "filter": "a.cat_slug === 'productivity'",
        "label": "Productivity",
    },
    "healthy-lifestyle/index.html": {
        "filter": "a.cat_slug === 'healthy-lifestyle'",
        "label": "Healthy Lifestyle",
    },
    "all-articles/index.html": {
        "filter": "true",
        "label": "All Articles",
    },
}

SORT_BAR_HTML = """
<div class="sort-bar">
  <div class="sort-bar-inner">
    <span class="sort-label">Sort by:</span>
    <div class="sort-btns">
      <button class="sort-btn active" data-sort="newest">Newest</button>
      <button class="sort-btn" data-sort="oldest">Oldest</button>
      <button class="sort-btn" data-sort="az">A &ndash; Z</button>
    </div>
    <span class="sort-count" id="article-count"></span>
  </div>
</div>
"""

SORT_CSS = """
<style>
.sort-bar { background: var(--bg); border-bottom: 1px solid var(--border); }
.sort-bar-inner { max-width: 1200px; margin: 0 auto; padding: 12px 24px; display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.sort-label { font-size: 0.78rem; font-weight: 600; color: var(--gray); white-space: nowrap; }
.sort-btns { display: flex; gap: 6px; }
.sort-btn { font-family: Poppins, sans-serif; font-size: 0.78rem; font-weight: 600; padding: 5px 14px; border-radius: 100px; border: 1.5px solid var(--border); background: transparent; color: var(--gray); cursor: pointer; transition: all 0.18s; }
.sort-btn:hover { border-color: var(--green); color: var(--green); }
.sort-btn.active { background: var(--dark); border-color: var(--dark); color: #fff; }
.sort-count { font-size: 0.75rem; color: var(--gray); margin-left: auto; }
</style>
"""

def build_script(filter_expr, label):
    return f"""<script>
  document.querySelectorAll('.cat-tab').forEach(tab => {{
    tab.addEventListener('click', function() {{ window.location.href = this.dataset.url; }});
  }});
  document.querySelectorAll('.sort-btn').forEach(btn => {{
    btn.addEventListener('click', function() {{
      document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      renderPage(1, this.dataset.sort);
    }});
  }});
  document.addEventListener('DOMContentLoaded', function() {{
    const PER_PAGE = 12;
    const allArticles = ARTICLES.filter(a => {filter_expr});
    const grid  = document.getElementById('article-grid');
    const empty = document.getElementById('empty-state');
    const pgEl  = document.getElementById('pagination');
    const countEl = document.getElementById('article-count');
    if (!allArticles.length) {{ grid.style.display='none'; empty.style.display='block'; return; }}

    function sorted(articles, mode) {{
      const arr = articles.slice();
      if (mode === 'oldest') return arr.reverse();
      if (mode === 'az') return arr.sort((a,b) => a.title.localeCompare(b.title));
      return arr; // newest (default, already newest-first in articles.js)
    }}

    function cardHTML(a) {{
      return `<div class="card">
        <picture><source srcset="../${{a.image.replace(".jpg",".webp")}}" type="image/webp"><img src="../${{a.image}}" alt="${{a.alt || a.title}}" style="width:100%;border-radius:8px 8px 0 0;display:block;object-fit:cover;height:200px;" loading="lazy"></picture>
        <div class="card-body">
          <span class="card-tag">${{a.category}}</span>
          <h3><a href="../articles/${{a.slug}}.html">${{a.title}}</a></h3>
          <p>${{a.excerpt}}</p>
          <div class="card-meta"><span>📅 ${{a.date}}</span><span>⏱ ${{a.read_time}} min read</span></div>
          <a href="../articles/${{a.slug}}.html" class="read-more">Read article &rarr;</a>
        </div>
      </div>`;
    }}

    window.renderPage = function(page, sortMode) {{
      sortMode = sortMode || document.querySelector('.sort-btn.active')?.dataset.sort || 'newest';
      const articles = sorted(allArticles, sortMode);
      const total = articles.length;
      const pages = Math.ceil(total / PER_PAGE);
      const start = (page - 1) * PER_PAGE;
      grid.innerHTML = articles.slice(start, start + PER_PAGE).map(cardHTML).join('');
      if (countEl) countEl.textContent = total + ' article' + (total !== 1 ? 's' : '');
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
      let html = `<button ${{page===1?'disabled':''}} onclick="renderPage(${{page-1}})">&laquo; Prev</button>`;
      for (let i = 1; i <= pages; i++) {{
        if (pages > 7 && Math.abs(i - page) > 2 && i !== 1 && i !== pages) {{
          if (i === page - 3 || i === page + 3) html += `<span class="pg-info">…</span>`;
          continue;
        }}
        html += `<button class="${{i===page?'active':''}}" onclick="renderPage(${{i}})">${{i}}</button>`;
      }}
      html += `<button ${{page===pages?'disabled':''}} onclick="renderPage(${{page+1}})">Next &raquo;</button>`;
      html += `<span class="pg-info">Page ${{page}} of ${{pages}}</span>`;
      pgEl.innerHTML = html;
    }};
    renderPage(1);
  }});
</script>"""


def upgrade_page(rel_path, filter_expr, label):
    filepath = os.path.join(BASE, rel_path)
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    # Add sort CSS in <head> if not already present
    if "sort-bar" not in html:
        html = html.replace("</head>", SORT_CSS + "</head>", 1)

    # Add sort bar after cat-tabs closing div
    if "sort-bar" not in html or "<div class=\"sort-bar\">" not in html:
        html = re.sub(
            r'(</div>\s*\n)(\s*<div class="container" style="padding-top:28px)',
            r'\1' + SORT_BAR_HTML + r'\2',
            html, count=1
        )

    # Replace the entire old script block
    new_script = build_script(filter_expr, label)
    # Remove old script
    html = re.sub(
        r'<script>\s*document\.querySelectorAll\(\'\.cat-tab\'\)[\s\S]*?</script>',
        new_script,
        html, count=1
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  Upgraded: {rel_path}")


def main():
    for rel_path, cfg in PAGES.items():
        upgrade_page(rel_path, cfg["filter"], cfg["label"])
    print("All category pages upgraded.")


if __name__ == "__main__":
    main()
