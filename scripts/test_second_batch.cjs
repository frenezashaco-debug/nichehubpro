const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const slugs=[...Object.keys(require('./second_batch_content.cjs').data),'foods-that-reduce-anxiety','natural-energy-boosters','why-hydration-affects-your-focus-more-than-you-think','how-to-build-energy-that-lasts-all-day-without-crashing','how-to-sleep-better-naturally'];
const cat=vm.runInNewContext(fs.readFileSync(path.join(root,'articles.js'),'utf8')+';ARTICLES');
const api=JSON.parse(fs.readFileSync(path.join(root,'api/articles.json'),'utf8'));
const plain=s=>s.replace(/<[^>]*>/g,' ').replace(/\s+/g,' ').trim();
for(const slug of slugs){
 const h=fs.readFileSync(path.join(root,'articles',slug+'.html'),'utf8');
 assert.equal((h.match(/<img\b/g)||[]).length,4,slug+' images');
 assert.equal((h.match(/class="faq-a"/g)||[]).length,5,slug+' FAQs');
 const meta=h.match(/<meta name="description" content="([^"]+)"/)[1];
 assert(meta.length>=155&&meta.length<=160,slug+' meta');
 const title=h.match(/<h1[^>]*>([^<]+)<\/h1>/)[1];
 assert.equal(cat.find(x=>x.slug===slug).title,title);assert.equal(api.find(x=>x.id===slug).shortText,meta);
 const ids=[...h.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);
 for(const m of h.matchAll(/href="#([^"]+)"/g))assert(ids.includes(m[1]),slug+' missing anchor '+m[1]);
 assert(!/—|TL;DR:|Images in this article are AI-generated illustrations\./.test(h),slug+' prohibited text');
 assert(h.includes('This article is for informational purposes only and does not replace professional medical advice.'));
 const schema=[...h.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)].map(m=>JSON.parse(m[1]));
 const faq=schema.find(x=>x['@type']==='FAQPage');assert(faq,slug+' FAQ schema');assert.equal(faq.mainEntity.length,5);
 const answers=[...h.matchAll(/<div class="faq-a">([\s\S]*?)<\/div>/g)].map(m=>plain(m[1]));
 faq.mainEntity.forEach((q,i)=>assert.equal(plain(q.acceptedAnswer.text),answers[i],slug+' FAQ mismatch'));
 const main=h.slice(h.indexOf('<article class='),h.indexOf('</article>'));
 assert(!/lowers cortisol by 20|dopamine for 16 hours|You don't need a diagnosis|submerge your face|Within six weeks, his decision|lost 3 pounds|By day four, Priya/.test(main),slug+' old claim');
}
console.log('PASS: ten guides, metadata/catalogues, four images each, five synchronized FAQs each, TOC anchors and targeted claim checks.');
