// Mechanical metadata repair only; never rewrites article content.
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const file = path.join(root,'api/articles.json');
const rows = JSON.parse(fs.readFileSync(file,'utf8'));
const categories = {'Mental Wellness':'mental_wellness','Productivity':'productivity','Healthy Lifestyle':'healthy_lifestyle'};
let changed=0;
for(const row of rows){
  if(!/^[a-z0-9-]+$/.test(row.id)) throw Error('Unexpected slug');
  const html=fs.readFileSync(path.join(root,'articles',row.id+'.html'),'utf8');
  const label=html.match(/<span\b[^>]*class=["']article-tag["'][^>]*>([^<]+)<\/span>/i)?.[1].trim();
  if(categories[label] && row.category!==categories[label]){
    console.log(`${row.id}: ${row.category} -> ${categories[label]}`);
    row.category=categories[label];changed++;
  }
}
fs.writeFileSync(file,JSON.stringify(rows,null,2)+'\n');
console.log(`${changed} categories synchronized; article text untouched.`);
