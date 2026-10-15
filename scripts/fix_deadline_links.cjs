// Exact legacy aliases found in the October 14 article; no broad redirects.
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const file=path.join(root,'articles/the-psychology-behind-why-deadlines-make-you-more-productive.html');
let html=fs.readFileSync(file,'utf8');
let changed=0;
for(const slug of ['how-to-protect-your-focus-from-constant-interruptions','best-time-management-techniques-ranked','how-to-stop-procrastinating-immediately','how-to-design-the-perfect-daily-routine','focus-vs-motivation-explained']){
 if(!fs.existsSync(path.join(root,'articles',slug+'.html')))throw Error('Missing destination '+slug);
 const old=`href='/${slug}'`, replacement=`href='/articles/${slug}.html'`;
 if(html.includes(old)){html=html.replaceAll(old,replacement);changed++;}
 else if(!html.includes(replacement))throw Error('Unexpected link '+slug);
}
fs.writeFileSync(file,html);
console.log(`${changed} legacy article links corrected.`);
