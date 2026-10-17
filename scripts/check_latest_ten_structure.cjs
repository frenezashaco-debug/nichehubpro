const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.join(__dirname,'..');
const latest=JSON.parse(fs.readFileSync(path.join(root,'api/articles.json'),'utf8')).sort((a,b)=>b.date.localeCompare(a.date)).slice(0,10);
for(const row of latest){
 const h=fs.readFileSync(path.join(root,'articles',row.id+'.html'),'utf8');
 const sections=[...h.matchAll(/<h2 id="sec-(\d+)">([^<]+)<\/h2>/g)];
 assert.equal(sections.length,5,row.id+': five main sections');
 [ /^what\b/i,/^what\b.*\bsigns\b/i,/^why\b/i,/^how\b/i,/^how\b.*\bdaily\b/i ].forEach((role,i)=>assert(role.test(sections[i][2])&&sections[i][2].endsWith('?'),row.id+': heading role '+(i+1)));
 assert(/\d/.test(h.match(/<h1>([^<]+)<\/h1>/)[1]),row.id+': numbered title');
 assert(h.indexOf('<div class="tldr">')<h.indexOf('<nav class="toc"'),row.id+': summary before navigation');
 for(let i=1;i<=5;i++)assert(h.includes('href="#sec-'+i+'"'),row.id+': navigation '+i);
 assert(!h.includes('href="#sec-6"'),row.id+': stale navigation');
 assert.equal((h.match(/<img\b/g)||[]).length,4);
 assert.equal((h.match(/class="faq-q"/g)||[]).length,5);
 assert(!/[\u2013\u2014\u2015]|&(?:mdash|ndash);|&#(?:8211|8212|8213);|&#x(?:2013|2014|2015);/i.test(h));
 assert(!/Images in this article are AI-generated illustrations|TL;DR\s*:/i.test(h));
 console.log('PASS '+row.id);
}
