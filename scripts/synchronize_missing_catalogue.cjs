// Add existing canonical API entries missing from the client-side registry.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.join(__dirname,'..'),file=path.join(root,'articles.js'),source=fs.readFileSync(file,'utf8');
const articles=vm.runInNewContext(source+';ARTICLES');
const api=JSON.parse(fs.readFileSync(path.join(root,'api/articles.json'),'utf8'));
const categories={mental_wellness:['Mental Wellness','mental-wellness'],productivity:['Productivity','productivity'],healthy_lifestyle:['Healthy Lifestyle','healthy-lifestyle']};
const decode=s=>s.replace(/&amp;/g,'&').replace(/&quot;/g,'"').replace(/&#39;/g,"'");
for(const row of api){
 if(articles.some(a=>a.slug===row.id))continue;
 if(!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(row.id))throw Error('Invalid slug');
 const h=fs.readFileSync(path.join(root,'articles',row.id+'.html'),'utf8');
 const img=h.match(/<img\b[^>]*src="([^"]+)"[^>]*>/);if(!img)throw Error('Missing cover '+row.id);
 const image=new URL(img[1],row.url);if(image.hostname!=='nichehubpro.com')throw Error('External cover');
 const [category,cat_slug]=categories[row.category]||[];if(!category)throw Error('Unknown category');
 const alt=img[0].match(/alt="([^"]*)"/)?.[1]||row.title;
 const articleBody=h.match(/<article\b[^>]*>([\s\S]*?)<\/article>/)?.[1]||h;
 const words=articleBody.replace(/<[^>]*>/g,' ').split(/\s+/).length;
 const date=new Date(row.date+'T12:00:00Z').toLocaleString('en-US',{month:'short',year:'numeric',timeZone:'UTC'});
 articles.push({slug:row.id,title:row.title,category,cat_slug,date,read_time:String(Math.max(1,Math.ceil(words/240))),excerpt:row.shortText,image:image.pathname.slice(1),alt:decode(alt),pins:[]});
 console.log('Added '+row.id);
}
const dates=new Map(api.map(r=>[r.id,r.date]));
articles.sort((a,b)=>(dates.get(b.slug)||'').localeCompare(dates.get(a.slug)||''));
fs.writeFileSync(file,source.slice(0,source.indexOf('const ARTICLES ='))+'const ARTICLES = '+JSON.stringify(articles,null,2)+';\n');
console.log('Catalogue entries: '+articles.length);
