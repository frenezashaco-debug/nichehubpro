const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.join(__dirname, '..');
const plain = text => text.replace(/<[^>]+>/g, ' ').replace(/&#x([a-f0-9]+);/gi, (_, n) => String.fromCodePoint(parseInt(n, 16)))
 .replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(Number(n))).replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&apos;/g, "'").replace(/&nbsp;/g, ' ').replace(/\s+/g, ' ').trim();
const errors = [];
let count = 0, schemas = 0;
for (const name of fs.readdirSync(path.join(root, 'articles')).filter(n => n.endsWith('.html'))) {
 const h = fs.readFileSync(path.join(root, 'articles', name), 'utf8');
 count++;
 try {
  assert(!/[\u2013\u2014\u2015]|&(?:mdash|ndash);|&#(?:8211|8212|8213);|&#x(?:2013|2014|2015);/i.test(h), 'forbidden dash form');
  assert(!/Images in this article are AI-generated illustrations/i.test(h), 'unwanted image boilerplate');
  assert.equal((h.match(/<img\b/g) || []).length, 4, 'four images');
  const faqs = [...h.matchAll(/<button\b[^>]*class="faq-q"[^>]*>([\s\S]*?)<span class="faq-icon">[\s\S]*?<div\b[^>]*class="faq-a"[^>]*>([\s\S]*?)<\/div>/g)].map(m => [plain(m[1]), plain(m[2])]);
  assert.equal(faqs.length, 5, 'five visible FAQ answers');
  for (const match of h.matchAll(/<script\b[^>]*type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/g)) {
   const data = JSON.parse(match[1]);
   const inspect = value => {
    if (!value || typeof value !== 'object') return;
    if (value['@type'] === 'FAQPage') {
     schemas++;
     assert.deepEqual(value.mainEntity.map(q => [plain(q.name), plain(q.acceptedAnswer.text)]), faqs, 'FAQ schema must match visible answers');
    }
    if (Array.isArray(value)) value.forEach(inspect);
    if (value['@graph']) value['@graph'].forEach(inspect);
   };
   inspect(data);
  }
  assert(!h.includes('../images/how-to-stop-worrying-about-the-future-sec1.webp'), 'watermarked image still referenced');
 } catch (error) { errors.push(name + ': ' + error.message); }
}
if (errors.length) throw Error(errors.join('\n'));
console.log(`PASS: ${count} articles, four images and five FAQs each, no forbidden dash forms or image boilerplate; ${schemas} FAQ schemas match visible answers.`);
