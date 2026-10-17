const fs = require('node:fs');
const path = require('node:path');
const corrections = require('./scientific_copy_corrections.cjs');
for (const [slug, edits] of Object.entries(require('./mechanism_copy_corrections.cjs'))) {
 corrections[slug] = [...(corrections[slug] || []), ...edits];
}
for (const [slug, edits] of Object.entries(require('./final_claim_corrections.cjs'))) {
 corrections[slug] = [...(corrections[slug] || []), ...edits];
}
for (const [slug, edits] of Object.entries(require('./anxiety_safety_corrections.cjs'))) {
 corrections[slug] = [...(corrections[slug] || []), ...edits];
}
for (const [slug, edits] of Object.entries(require('./remaining_safety_corrections.cjs'))) {
 corrections[slug] = [...(corrections[slug] || []), ...edits];
}
for (const [slug, edits] of Object.entries(require('./metabolic_reward_corrections.cjs'))) {
 corrections[slug] = [...(corrections[slug] || []), ...edits.sort((a, b) => b[0].length - a[0].length)];
}
const root = path.join(__dirname, '..');
const decode = value => value.replace(/&#x([a-f0-9]+);/gi, (_, n) => String.fromCodePoint(parseInt(n, 16)))
 .replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(Number(n)))
 .replace(/&quot;/g, '"').replace(/&apos;|&#39;/g, "'").replace(/&amp;/g, '&').replace(/&nbsp;/g, ' ');
const visible = value => decode(value.replace(/<[^>]+>/g, ' ')).replace(/\s+/g, ' ').trim();
const plans = [];
const missing = [];
let count = 0;
for (const [slug, edits] of Object.entries(corrections)) {
 const file = path.join(root, 'articles', slug + '.html');
 const original = fs.readFileSync(file, 'utf8');
 let html = original;
 for (const [prefix, replacement] of edits) {
  let found = 0;
  for (const pattern of [/(<p\b[^>]*>)([\s\S]*?)(<\/p>)/g, /(<li\b[^>]*>)([\s\S]*?)(<\/li>)/g, /(<div\b[^>]*class="faq-a"[^>]*>)([\s\S]*?)(<\/div>)/g]) {
   html = html.replace(pattern, (full, start, content, end) => {
    if (visible(content) === visible(replacement)) return full;
    if (!visible(content).startsWith(prefix)) return full;
    found++;
    return start + replacement + end;
   });
  }
  if (found > 1) throw Error('Ambiguous block: ' + slug + ': ' + prefix);
  if (!found && !html.includes(replacement)) missing.push(slug + ': ' + prefix);
  count += found;
 }
 // Keep machine-readable answers aligned with visible corrected answers.
 const questions = [...html.matchAll(/<button class="faq-q">([\s\S]*?)<span class="faq-icon">[\s\S]*?<div class="faq-a">([\s\S]*?)<\/div>/g)]
  .map(m => ({'@type': 'Question', name: visible(m[1]), acceptedAnswer: {'@type': 'Answer', text: visible(m[2])}}));
 html = html.replace(/(<script\b[^>]*type="application\/ld\+json"[^>]*>)([\s\S]*?)(<\/script>)/g, (full, open, text, close) => {
  const data = JSON.parse(text);
  const update = item => {
   if (!item || typeof item !== 'object') return;
   if (item['@type'] === 'FAQPage') {
    if (questions.length !== 5) throw Error('Expected five visible FAQ answers: ' + slug);
    item.mainEntity = questions;
   }
   if (item['@type'] === 'Article') item.dateModified = '2026-10-17';
   if (Array.isArray(item)) item.forEach(update);
   if (item['@graph']) item['@graph'].forEach(update);
  };
  update(data);
  return open + JSON.stringify(data, null, 2) + close;
 });
 plans.push({slug, file, original, html});
}
// Validate every target before writing any file.
if (missing.length) throw Error('Missing targets:\n' + missing.join('\n'));
for (const {file, html, original} of plans) if (html !== original) fs.writeFileSync(file, html);
const report = {date: '2026-10-17', targeted_blocks_configured: Object.values(corrections).reduce((n, edits) => n + edits.length, 0), changes_this_run: count, articles: plans.map(({slug}) => slug), scope: 'Specific unsupported claims corrected. Remaining claims require review.'};
fs.mkdirSync(path.join(root, 'reports'), {recursive: true});
fs.writeFileSync(path.join(root, 'reports/scientific-copy-corrections.json'), JSON.stringify(report, null, 2));
console.log(`Corrected ${count} identified blocks across ${plans.length} articles; FAQ schema synchronized.`);
