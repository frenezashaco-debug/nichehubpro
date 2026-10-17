const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.join(__dirname, '..');
const corrected = new Set([
 ...Object.keys(require('./scientific_copy_corrections.cjs')),
 ...Object.keys(require('./mechanism_copy_corrections.cjs')),
 ...Object.keys(require('./final_claim_corrections.cjs')),
 ...Object.keys(require('./anxiety_safety_corrections.cjs')),
 ...Object.keys(require('./remaining_safety_corrections.cjs')),
 ...Object.keys(require('./metabolic_reward_corrections.cjs'))
]);
const descriptions = {
 'how-blood-sugar-swings-affect-your-energy-and-mood': 'How blood sugar swings affect your energy and mood: distinguish symptoms from a diagnosis, prepare a record, and know when to seek appropriate medical care.',
 'how-dopamine-actually-works-and-why-quick-fixes-backfire': 'How dopamine actually works and why quick fixes backfire: separate neuroscience from habit claims, review daily choices, and seek support when symptoms persist.',
 'how-to-stop-negative-thoughts': 'How to stop negative thoughts: notice recurring worries, try a balanced thought record, and choose practical next steps, with guidance on when to seek support.',
 'how-to-build-confidence': 'How to build confidence: prepare a manageable task, practise with feedback, and review self-doubt using practical steps that fit your circumstances and support.',
 'how-to-reduce-anxiety-naturally': 'How to reduce anxiety naturally: consider comfortable self-care options, understand their limits, and find guidance on when to seek professional assessment.'
};
const jsFile = path.join(root, 'articles.js');
const originalJs = fs.readFileSync(jsFile, 'utf8');
const catalogue = vm.runInNewContext(originalJs + ';ARTICLES');
const apiFile = path.join(root, 'api/articles.json');
const api = JSON.parse(fs.readFileSync(apiFile, 'utf8'));
let sitemap = fs.readFileSync(path.join(root, 'sitemap.xml'), 'utf8');
let styleChanges = 0;
for (const name of fs.readdirSync(path.join(root, 'articles')).filter(f => f.endsWith('.html'))) {
 const file = path.join(root, 'articles', name), slug = name.slice(0, -5);
 let h = fs.readFileSync(file, 'utf8');
 const before = h;
 // Idempotent mechanical style cleanup, including numeric entity variants.
 h = h.replace(/[\u2013\u2014\u2015]|&(?:mdash|ndash);|&#(?:8211|8212|8213);|&#x(?:2013|2014|2015);/gi, '-');
 h = h.replace(/\bproven (?=(?:techniques|methods|ways|strategies|habits|tools|steps)\b)/gi, 'practical ');
 if (h !== before) { styleChanges++; corrected.add(slug); }
 if (descriptions[slug]) {
  let description = descriptions[slug];
  if (description.length < 155) description += ' Read more.';
  if (description.length < 155 || description.length > 160) throw Error('Meta length: ' + slug + ' ' + description.length);
  h = h.replace(/(<meta (?:name="description"|property="og:description") content=")[^"]*(")/g, '$1' + description + '$2');
  h = h.replace(/("description"\s*:\s*")[^"]*(")/, '$1' + description + '$2');
 }
 if (corrected.has(slug)) {
  h = h.replace(/("dateModified"\s*:\s*")[^"]+"/g, '$12026-10-17"');
  const meta = h.match(/<meta name="description" content="([^"]+)"/)[1];
  const row = catalogue.find(r => r.slug === slug), item = api.find(r => r.id === slug);
  if (row) {
   row.excerpt = meta;
   if (row.pins) row.pins = row.pins.map(pin => ({...pin, description: meta}));
  }
  if (item) item.shortText = meta;
  const url = 'https://nichehubpro.com/articles/' + slug + '.html';
  sitemap = sitemap.replace(/<url>[\s\S]*?<\/url>/g, block => block.includes('<loc>' + url + '</loc>') ? block.replace(/<lastmod>[^<]+<\/lastmod>/, '<lastmod>2026-10-17</lastmod>') : block);
 }
 if (h !== before) fs.writeFileSync(file, h);
}
const js = originalJs.slice(0, originalJs.indexOf('const ARTICLES =')) + 'const ARTICLES = ' + JSON.stringify(catalogue, null, 2) + ';\n';
fs.writeFileSync(jsFile, js);
fs.writeFileSync(apiFile, JSON.stringify(api, null, 2) + '\n');
fs.writeFileSync(path.join(root, 'sitemap.xml'), sitemap);
console.log(`All article HTML checked for forbidden dash forms. ${styleChanges} additional files received wording/style cleanup. Catalogue summaries and sitemap synchronized for ${corrected.size} revised articles.`);
