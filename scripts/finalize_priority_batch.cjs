const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const fixes={
'how-to-build-a-stress-resistant-morning-routine':{
0:'There is no required duration. Choose one useful action that fits your schedule without shortening sleep, and add more only if it remains manageable.',
1:'There is no single highest-impact habit for everyone. Identify your main practical obstacle, such as searching for essentials or responding to optional messages, and address that first.',
2:'A routine can organize tasks, but this guide does not establish changes in cortisol or brain activity. Judge a small adjustment by its practical usefulness; seek help for persistent anxiety.',
3:'Yes, a plan can fit a later start or shift work. Protect adequate sleep and necessary care rather than following a fixed morning window.'},
'how-to-stay-motivated':{
0:'Reduce unnecessary demands and seek professional support when anxiety or low mood affects daily life. A small task may be manageable, but completing it is not a treatment or a test of recovery.',
2:'Motivation depends on more than a learned skill. Health, available time, resources, interest, and support can all matter. Work on an identifiable obstacle rather than trying to manage dopamine.',
3:'There is no reliable recovery deadline. Try a manageable next step, review what made it possible or difficult, and seek support when the problem persists.',
4:'Motivation describes wanting to act; a routine can organize action when enthusiasm varies. Neither discipline nor a system removes health limits or competing responsibilities. Adjust the demand when needed.'},
'how-to-reset-your-mindset':{
1:'A small self-directed exercise may be useful, but there is no need to wait months before seeking therapy or another assessment. Ask for support when distress or impaired functioning concerns you.',
3:'Recurring negative thoughts can have different explanations. A blog cannot identify a neural pathway or a single cause. Describe the pattern and its impact to a qualified professional if it persists.',
4:'There is no universally best technique. You could try a brief external grounding exercise or a structured note if comfortable. Stop if it increases distress and consider individualized support.'},
'best-morning-habits-for-more-energy':{
0:'Start with adequate opportunity for sleep and a realistic morning schedule. Food, fluids, and comfortable activity should fit your individual needs, not a promise to boost hormones.',
1:'There is no reliable timeline. Review whether a change solves a practical problem, and seek an assessment for persistent fatigue rather than waiting for habits to cure it.',
2:'Choose a time that fits your health, schedule, and sleep. This article does not establish that morning exercise is superior for everyone. Adjust activity if it interferes with sleep or causes concerning symptoms.',
3:'Sleep duration alone cannot identify the cause of tiredness. If fatigue persists or affects daily activities, discuss sleep quality, symptoms, medicines, and other factors with a healthcare professional.',
4:'Choose food you can access and tolerate, consistent with any medical advice. No breakfast guarantees steady energy or prevents a blood sugar problem. Ask for individualized advice if needed.'},
'how-to-stop-self-sabotaging':{
1:'Examples include delaying a task, avoiding a difficult conversation, or setting unrealistic standards. These behaviors do not all serve the same purpose. Note the context and consequence before assuming a cause.'},
'how-to-improve-concentration-naturally':{
3:'Effort is only one part of the situation. Check task clarity, interruptions, rest, and health needs; changing the environment is an experiment, not a guaranteed fix.',
4:'Attention difficulties can have several causes, and this article cannot determine which applies. A qualified professional can assess persistent difficulties and whether ADHD or something else is involved.'},
'best-focus-techniques-for-students':{
0:'Try a clear task with a manageable stopping point. A timer may help, but it can also interrupt useful work. Compare completed work and accuracy rather than expecting one method to suit every student.',
1:'There is no universal study interval. Start with a length that fits the assignment, take a break when needed, and adjust based on comprehension and fatigue rather than a supposed biological cycle.',
2:'Test quiet and music on comparable tasks and check your errors and comprehension. Keep the option that helps your work rather than assuming one sound environment is best.',
3:'If optional phone use repeatedly interrupts you, try placing it out of reach or silencing nonessential notifications. Keep necessary communication and accessibility tools available.',
4:'List deadlines and requirements, then choose one concrete task. Break an unclear assignment into a question you can answer, and ask a teacher for clarification when needed.'}
};
for(const [slug,answers]of Object.entries(fixes)){
 const file=path.join(root,'articles',slug+'.html');let html=fs.readFileSync(file,'utf8'),i=0;
 html=html.replace(/(<div class="faq-a">)([\s\S]*?)(<\/div>)/g,(_,a,b,c)=>a+(answers[i++]??b)+c);
 if(i!==5)throw Error('Unexpected FAQ count '+slug);
 fs.writeFileSync(file,html);
}
for(const slug of ['how-to-stop-panic-attacks','morning-routine-for-a-healthy-lifestyle']){
 const file=path.join(root,'articles',slug+'.html');let html=fs.readFileSync(file,'utf8');
 html=html.replace(/<div class="sources-card"[^>]*>\s*<p[^>]*>Evidence-based references<\/p>[\s\S]*?<\/ul>\s*<\/div>/,'');
 const box=html.match(/<div class="sources-box">[\s\S]*?<\/ul><\/div>/)?.[0];if(!box)throw Error('Sources missing');
 html=html.replace(box,'');
 // Keep sources within the article, before the final disclaimer.
 const index=html.search(/<div[^>]*>\s*<strong\b[^>]*>(?:Medical )?Disclaimer:/);if(index<0)throw Error('Disclaimer missing');
 html=html.slice(0,index)+box+html.slice(index);
 fs.writeFileSync(file,html);
}
// Refresh only modification dates in sitemap; publication dates remain unchanged.
const slugs=[...Object.keys(fixes),'how-to-control-your-thoughts','how-to-stop-panic-attacks','morning-routine-for-a-healthy-lifestyle'];
let sitemap=fs.readFileSync(path.join(root,'sitemap.xml'),'utf8');
for(const slug of slugs){
 const re=new RegExp('(<loc>https://nichehubpro.com/articles/'+slug+'\\.html</loc>\\s*<lastmod>)[^<]+');
 if(!re.test(sitemap))throw Error('Missing sitemap date '+slug);
 sitemap=sitemap.replace(re,'$12026-10-14');
}
fs.writeFileSync(path.join(root,'sitemap.xml'),sitemap);
console.log('FAQ residuals, source positioning and sitemap modification dates updated.');
