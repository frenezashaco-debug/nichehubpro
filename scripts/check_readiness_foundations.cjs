const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.join(__dirname,'..'),read=file=>fs.readFileSync(path.join(root,file),'utf8');
const articles=vm.runInNewContext(read('articles.js')+';ARTICLES'),api=JSON.parse(read('api/articles.json'));
assert.equal(articles.length,api.length);
assert(api.every(row=>articles.some(a=>a.slug===row.id)),'complete catalogue');
for(const [hub,category] of Object.entries({'all-articles':null,'mental-wellness':'mental-wellness','productivity':'productivity','healthy-lifestyle':'healthy-lifestyle'})){
 const h=read(hub+'/index.html'),cards=h.match(/<!-- STATIC_ARTICLE_CARDS_START -->([\s\S]*?)<!-- STATIC_ARTICLE_CARDS_END -->/)[1];
 const expected=articles.filter(a=>category===null||a.cat_slug===category);
 assert.equal((cards.match(/class="card"/g)||[]).length,expected.length);
 for(const row of expected)assert(cards.includes('href="/articles/'+row.slug+'.html"'));
 assert(!h.includes('end-form/build/main.js'),'subscription confirmation remains with native provider');
}
for(const file of ['contact.html','contact/index.html']){
 const h=read(file);assert(h.includes('id="contact-form" action="https://formspree.io/f/mojyklpq" method="POST"'));
 for(const name of ['name','email','subject','message'])assert(h.includes('name="'+name+'"'));
 assert(h.includes('/contact.js?v=readiness-v1'));assert(!h.includes('function handleContact'));
 assert(!h.includes('reply within 2 business days'));
}
for(const file of ['privacy.html','privacy/index.html']){
 const h=read(file);assert(h.includes('nhp-analytics-choice-v1'));assert(h.includes('Formspree'));assert(h.includes('Brevo'));
 assert(h.includes('not a certified advertising consent management platform'));assert(!h.includes('collects anonymized data'));
}
assert(!read('script.js').includes("mode: 'no-cors'"));
assert(read('ads.txt').trim()==='google.com, pub-7481817319849340, DIRECT, f08c47fec0942fa0');
console.log('PASS: complete catalogue/static hubs, real contact forms, native subscription flow and consistent privacy copy. CMP and delivery still require live/account checks.');
