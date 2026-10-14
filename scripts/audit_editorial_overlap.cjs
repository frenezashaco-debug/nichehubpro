// Triage only: exact repeated prose is not a Google low-value classification.
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const clean = s => s.replace(/<[^>]*>/g, ' ').replace(/&nbsp;/g, ' ').replace(/\s+/g, ' ').trim();
const paragraphs = new Map();
const articles = [];
for (const file of fs.readdirSync(path.join(root, 'articles')).filter(f => f.endsWith('.html')).sort()) {
  const html = fs.readFileSync(path.join(root, 'articles', file), 'utf8');
  const body = html.match(/<article\b[^>]*>([\s\S]*?)<\/article>/i)?.[1];
  if (!body) continue;
  // Exclude author/reference/disclaimer/footer boilerplate and FAQ.
  const prose = body.split(/<div class="author-block|<div class="references|<h2[^>]*id="faq"/i)[0];
  const ps = [...prose.matchAll(/<p\b[^>]*>([\s\S]*?)<\/p>/gi)].map(m => clean(m[1]));
  for (const p of new Set(ps.filter(p => p.split(' ').length >= 25))) {
    const entries = paragraphs.get(p) || []; entries.push(file); paragraphs.set(p, entries);
  }
  articles.push({file, words: clean(prose).split(/\s+/).length, images: (body.match(/<img\b/gi)||[]).length});
}
const repeated = [...paragraphs].filter(([,files]) => files.length > 1).map(([text,files])=>({text,files})).sort((a,b)=>b.files.length-a.files.length);
const report = {scope:'Local article main prose; exact repetition only. Not factual review or an AdSense verdict.', scanned:articles.length, repeatedParagraphs:repeated.length, affectedArticles:new Set(repeated.flatMap(p=>p.files)).size, repeated, articles};
fs.mkdirSync(path.join(root,'reports'),{recursive:true});
fs.writeFileSync(path.join(root,'reports','editorial-overlap.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({scanned:report.scanned,repeatedParagraphs:report.repeatedParagraphs,affectedArticles:report.affectedArticles,examples:repeated.slice(0,5)},null,2));
