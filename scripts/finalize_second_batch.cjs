const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const slugs=[...Object.keys(require('./second_batch_content.cjs').data),'foods-that-reduce-anxiety','natural-energy-boosters','why-hydration-affects-your-focus-more-than-you-think','how-to-build-energy-that-lasts-all-day-without-crashing','how-to-sleep-better-naturally'];
const jsFile=path.join(root,'articles.js'), apiFile=path.join(root,'api/articles.json');
const original=fs.readFileSync(jsFile,'utf8');
const catalogue=vm.runInNewContext(original+';ARTICLES');
const api=JSON.parse(fs.readFileSync(apiFile,'utf8'));
let sitemap=fs.readFileSync(path.join(root,'sitemap.xml'),'utf8');
for(const slug of slugs){
 const file=path.join(root,'articles',slug+'.html');let h=fs.readFileSync(file,'utf8');
 const title=h.match(/<h1[^>]*>([^<]+)<\/h1>/)[1];
 const description=h.match(/<meta name="description" content="([^"]+)"/)[1];
 const body=h.slice(h.indexOf('<article class='),h.indexOf('</article>'));
 const readTime=String(Math.ceil(body.replace(/<[^>]*>/g,' ').split(/\s+/).length/220));
 h=h.replace(/("dateModified"\s*:\s*")[^"]+"/g,'$12026-10-16"');
 h=h.replace(/(<span id="read-time">)\d+(<\/span>)/,'$1'+readTime+'$2');
 h=h.replace('<h3>Sources and scope</h3>','<h3>Sources &amp; References</h3>');
 h=h.replace(/[ \t]+$/gm,'');
 if(!h.includes('"@type":"FAQPage"')&&!h.includes('"@type": "FAQPage"')){
  const clean=s=>s.replace(/<[^>]*>/g,' ').replace(/\s+/g,' ').trim();
  const questions=[...h.matchAll(/<button class="faq-q">([\s\S]*?)<span class="faq-icon">[\s\S]*?<div class="faq-a">([\s\S]*?)<\/div>/g)].map(m=>({'@type':'Question',name:clean(m[1]),acceptedAnswer:{'@type':'Answer',text:clean(m[2])}}));
  if(questions.length!==5)throw Error('Missing visible FAQs '+slug);
  h=h.replace('</head>','<script type="application/ld+json">'+JSON.stringify({'@context':'https://schema.org','@type':'FAQPage',mainEntity:questions})+'</script>\n</head>');
 }
 fs.writeFileSync(file,h);
 const row=catalogue.find(x=>x.slug===slug), entry=api.find(x=>x.id===slug);
 if(!row||!entry)throw Error('Missing catalogue entry '+slug);
 row.title=title;row.excerpt=description;row.read_time=readTime;
 // Replace old promotional claims too, without sending any pins.
 if(row.pins)row.pins=row.pins.map((pin,i)=>({...pin,title:i===0?title:i===1?'Planning checklist: '+title.split(':')[0]:'Practical questions: '+title.split(':')[0],description}));
 entry.title=title;entry.shortText=description;
 const url='https://nichehubpro.com/articles/'+slug+'.html';
 let found=0;
 sitemap=sitemap.replace(/<url>[\s\S]*?<\/url>/g,block=>{if(!block.includes('<loc>'+url+'</loc>'))return block;found++;return block.replace(/<lastmod>[^<]+<\/lastmod>/,'<lastmod>2026-10-16</lastmod>');});
 if(found!==1)throw Error('Sitemap match '+slug);
}
fs.writeFileSync(jsFile,original.slice(0,original.indexOf('const ARTICLES ='))+'const ARTICLES = '+JSON.stringify(catalogue,null,2)+';\n');
fs.writeFileSync(apiFile,JSON.stringify(api,null,2)+'\n');
fs.writeFileSync(path.join(root,'sitemap.xml'),sitemap);
console.log('Synchronized ten article titles, summaries, read times, pin copy, and sitemap dates. No publication triggered.');
