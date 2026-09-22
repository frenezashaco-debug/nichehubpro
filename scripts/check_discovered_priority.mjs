// Read-only regression checks for the September 22 editorial/linking batch.
// Run from the repository root: node scripts/check_discovered_priority.mjs
import fs from 'node:fs';
import assert from 'node:assert/strict';
import vm from 'node:vm';

const base = 'https://nichehubpro.com';
const targets = ['/articles/best-free-productivity-apps-for-android-2026.html',
  '/anxiety-and-stress/', '/sleep-and-energy/',
  '/articles/how-to-stop-overthinking-at-work.html', '/overthinking/'];
const baseline = [1, 2, 2, 3, 4];
const local = path => '.' + path + (path.endsWith('/') ? 'index.html' : '');
const sitemap = fs.readFileSync('sitemap.xml', 'utf8');
const urls = [...sitemap.matchAll(/<loc>(.*?)<\/loc>/g)].map(m => m[1]);
assert.equal(new Set(urls).size, urls.length, 'Duplicate sitemap URL');
const incoming = new Map(targets.map(t => [t, new Set()]));
for (const url of urls) {
  const html = fs.readFileSync(local(new URL(url).pathname), 'utf8');
  for (const [, href] of html.matchAll(/<a\b[^>]*href=["']([^"']+)/g)) {
    const dest = new URL(href.replaceAll('&amp;', '&'), url);
    if (dest.origin === base && incoming.has(dest.pathname) && url !== base + dest.pathname)
      incoming.get(dest.pathname).add(url);
  }
}
const articles = JSON.parse(fs.readFileSync('api/articles.json', 'utf8'));
for (const [i, path] of targets.entries()) {
  const html = fs.readFileSync(local(path), 'utf8');
  assert(urls.includes(base + path), `Not in sitemap: ${path}`);
  assert(html.includes(`rel="canonical" href="${base + path}"`));
  assert(!/<meta[^>]*content=["'][^"']*noindex/i.test(html));
  assert(incoming.get(path).size > baseline[i], `No increase in referring pages: ${path}`);
  for (const [, href] of html.matchAll(/<a\b[^>]*href=["']([^"']+)/g)) {
    const url = new URL(href.replaceAll('&amp;', '&'), base + path);
    if (url.origin === base) assert(fs.existsSync(local(url.pathname)), `Missing local link: ${url}`);
  }
  if (path.startsWith('/articles/')) {
    const body = html.match(/<article[^>]*id="article-body">([\s\S]*?)<\/article>/)[1];
    assert.equal((body.match(/class="faq-item"/g) || []).length, 5);
    assert(body.includes('id="sources"'));
    assert(!/Sarah spent|30\+ minutes|40%|60%|23%|rewiring|ranked by real use/i.test(body));
    assert(!body.includes('\u2014'));
    const desc = html.match(/name="description" content="([^"]*)"/)[1];
    assert(desc.length >= 155 && desc.length <= 160);
    const data = [...html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)]
      .map(m => JSON.parse(m[1]));
    const article = data.find(d => d['@type'] === 'Article');
    assert.equal(article.description, desc);
    assert.equal(article.dateModified, '2026-09-22');
    assert.equal(articles.find(a => a.url === base + path).shortText, desc);
  }
  console.log(`${path}: referring pages ${baseline[i]} -> ${incoming.get(path).size}`);
}

// Test FAQ state transitions using the actual two handler implementations.
const sources = [fs.readFileSync('script.js', 'utf8'),
  fs.readFileSync(local(targets[0]), 'utf8')];
for (const source of sources) {
  const start = source.indexOf("document.querySelectorAll('.faq-q').forEach");
  const end = source.indexOf('\n});', start) >= 0 && source.includes('const bar =')
    ? source.indexOf('\nconst bar =', start)
    : source.indexOf('// ── READING TIME', start);
  assert(start >= 0 && end > start);
  const items = Array.from({length: 2}, () => {
    const classes = new Set();
    const button = {attrs: {}, setAttribute(k,v) { this.attrs[k] = v; },
      addEventListener(_, fn) { this.click = fn; }};
    const item = {classList: {contains: k => classes.has(k), add: k => classes.add(k),
      remove: k => classes.delete(k)}, querySelector: () => button};
    button.closest = () => item;
    return {item, button};
  });
  vm.runInNewContext(source.slice(start, end), {document: {
    querySelectorAll: q => items.map(x => q === '.faq-q' ? x.button : x.item)
  }});
  items[0].button.click();
  assert.equal(items[0].button.attrs['aria-expanded'], 'true');
  items[1].button.click();
  assert.equal(items[0].button.attrs['aria-expanded'], 'false');
  assert.equal(items[1].button.attrs['aria-expanded'], 'true');
  items[1].button.click();
  assert.equal(items[1].button.attrs['aria-expanded'], 'false');
}
console.log('PASS: local destinations, metadata, five FAQ items, sources, and accordion transitions.');
