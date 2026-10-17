// One-time, idempotent regrouping. Preserve all existing advice and safety text.
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const root = path.join(__dirname, '..');
const profiles = {
 'how-sleep-debt-silently-drains-your-daily-performance': {
  topic:'sleep debt', order:[[1],[3],[2],[4],[5,6]],
  headings:['What Is Sleep Debt?','What Are the Signs of Insufficient Sleep?','Why Does Sleep Debt Affect Daily Performance?','How Can You Address an Unsustainable Sleep Schedule?','How Can You Manage Sleep Habits Daily?'],
  title:'How Sleep Debt Silently Drains Your Daily Performance: 5 Practical Checks'},
 'the-psychology-behind-why-deadlines-make-you-more-productive': {
  order:[[1],[2],[3],[4],[5]], headings:['What Is a Deadline and How Does It Differ From a Work Block?','What Are the Signs a Deadline Is Helping or Hurting?','Why Can the Same Time Limit Work Differently Across Tasks?','How Can You Fix an Unrealistic Deadline Plan?','How Can You Review Deadline Use Daily?']},
 'what-cognitive-load-does-to-your-decision-making': {
  order:[[1],[3],[4],[2],[5,6]], headings:['What Is Cognitive Load?','What Are the Signs a Decision Needs a Pause?','Why Does Mental Effort Feel Harder Sometimes?','How Can You Make a Complicated Decision Easier?','How Can You Manage Decisions Daily?']},
 'how-blood-sugar-swings-affect-your-energy-and-mood': {
  order:[[],[2],[1,3],[4,5],[6]],
  headings:['What Are Blood Glucose Changes?','What Are the Signs That Need Assessment?','Why Can Energy and Mood Change Around Meals?','How Can You Respond Safely to Recurrent Symptoms?','How Can You Manage Concerns About Glucose Daily?'],
  extra:'<p>Blood glucose describes the glucose circulating in the blood, not a feeling of energy. Symptoms such as tiredness or irritability do not establish a glucose problem. Use the assessment and monitoring advice already provided by your clinician.</p><ul><li>Describe the symptoms rather than diagnosing a crash.</li><li>Keep existing diabetes treatment instructions available if they apply to you.</li><li>Discuss recurring unexplained episodes with a qualified clinician.</li></ul>',
  title:'How Blood Sugar Swings Affect Your Energy and Mood: 5 Practical Checks'},
 'how-dopamine-actually-works-and-why-quick-fixes-backfire': {
  order:[[1],[2],[3],[4],[5,6]], headings:['What Is Dopamine?','What Are the Signs a Quick-Fix Habit Is Becoming a Problem?','Why Can an Immediate Option Feel Easier?','How Can You Change a Habit That Interferes With Your Priorities?','How Can You Review Reward-Seeking Habits Daily?'],
  title:'How Dopamine Actually Works and Why Quick Fixes Backfire: 5 Practical Checks'},
 'how-to-train-your-brain-for-longer-attention-spans': {
  order:[[1],[2],[3],[4],[5,6]], headings:['What Does Training Your Attention Actually Mean?','What Are the Signs Your Focus Setup Needs Adjusting?','Why Does Attention Drift During a Task?','How Can You Reset When Your Attention Wanders?','How Can You Manage Focus Practice Daily?']},
 'how-your-body-clock-affects-when-you-should-exercise': {
  order:[[1],[2],[3],[4],[5]], headings:['What Is the Connection Between Your Body Clock and Exercise Timing?','What Are the Signs That Your Exercise Time Does Not Fit?','Why Does Choosing an Exercise Time Feel Difficult?','How Can You Fix an Exercise Schedule That Keeps Falling Apart?','How Can You Manage Exercise Timing Daily?']},
 'how-to-stop-feeling-guilty-for-resting': {
  order:[[],[2],[1,3],[4],[5,6]], headings:['What Is Guilt About Resting?','What Are the Signs Rest Guilt Is Affecting You?','Why Can Taking a Break Feel Difficult?','How Can You Respond to Guilt About Resting?','How Can You Make Room for Rest Daily?'],
  extra:'<p>Guilt about resting means judging yourself for pausing even when a break fits your needs. The feeling alone does not establish a mental health diagnosis. Notice the specific thought and consider what you would advise someone in the same situation.</p><ul><li>Name the responsibility that is worrying you.</li><li>Distinguish an urgent task from a rule that you must always be busy.</li><li>Choose a manageable break and arrange any necessary cover first.</li></ul>'},
 'the-science-of-habit-formation-explained-simply': {
  order:[[1],[],[2,3],[4,5],[6]], headings:['What Is the Habit Loop?','What Are the Signs a Routine Is Becoming Automatic?','Why Can Changing a Habit Be Difficult?','How Can You Build a More Workable Habit?','How Can You Support a Habit Daily?'],
  extra:'<p>A routine can feel more automatic when a familiar situation prompts the same action with less deliberate planning. This is an observation about behavior, not a measurement of brain change. Record the situation and action before deciding what to adjust.</p><ul><li>Notice whether the action follows a repeated cue.</li><li>Check whether the routine still serves your goal.</li><li>Prepare a small alternative when the existing action gets in the way.</li></ul>'},
 'how-to-build-energy-that-lasts-all-day-without-crashing': {
  order:[[],[],[1,2],[4,5],[3,6]], headings:['What Is a Workable Daily Energy Routine?','What Are the Signs Your Routine Needs Review?','Why Can Your Energy Vary Across the Day?','How Can You Adjust a Routine That Leaves You Exhausted?','How Can You Manage Daily Energy Without Rigid Rules?'],
  extras:[
   '<p>A daily energy routine is a practical plan for meals, sleep, activity and workload, not a promise of constant alertness. Energy can vary across the day for different reasons. Choose one part of your schedule to review rather than expecting a perfect day.</p><ul><li>Set realistic demands for the time available.</li><li>Include opportunities for food, rest and ordinary movement.</li><li>Seek assessment for persistent or unexplained fatigue.</li></ul>',
   '<p>A pattern of missed breaks or difficult mornings is useful information, but it does not identify a medical cause. Note when tiredness happens and what it prevents you from doing. Bring persistent or concerning symptoms to a qualified clinician.</p><ul><li>Record activities that repeatedly leave you unable to continue.</li><li>Notice sleep difficulties and changing demands without assuming a diagnosis.</li><li>Review whether your plan includes enough time for basic needs.</li></ul>']}
};
const latest = JSON.parse(fs.readFileSync(path.join(root,'api/articles.json'),'utf8')).sort((a,b)=>b.date.localeCompare(a.date)).slice(0,10);
const cataloguePath=path.join(root,'articles.js'), catalogueText=fs.readFileSync(cataloguePath,'utf8');
const catalogue=vm.runInNewContext(catalogueText+';ARTICLES');
const apiPath=path.join(root,'api/articles.json'), api=JSON.parse(fs.readFileSync(apiPath,'utf8'));
let sitemap=fs.readFileSync(path.join(root,'sitemap.xml'),'utf8');
let homepage=fs.readFileSync(path.join(root,'index.html'),'utf8');
for(const row of latest){
 const profile=profiles[row.id]; if(!profile)throw Error('Missing profile '+row.id);
 const file=path.join(root,'articles',row.id+'.html');let h=fs.readFileSync(file,'utf8');
 if(!h.includes('<!-- five-section-review:2026-10-17 -->')){
  const start=h.search(/<h2 id="sec-1">/), end=h.indexOf('<h2 id="real-life">');
  const fallback=h.indexOf('<div class="author-block"',start);
  const finish=end>=0?end:fallback;if(start<0||finish<0)throw Error('Section boundaries '+row.id);
  const region=h.slice(start,finish), positions=[...region.matchAll(/<h2 id="sec-(\d+)">([^<]+)<\/h2>/g)];
  const blocks=new Map(positions.map((m,i)=>[Number(m[1]),{heading:m[2],body:region.slice(m.index+m[0].length,i+1<positions.length?positions[i+1].index:region.length)}]));
  const used=profile.order.flat();if(used.length!==blocks.size||new Set(used).size!==blocks.size)throw Error('Would lose section '+row.id);
  const sections=profile.order.map((group,i)=>{
   const body=group.length?group.map((num,j)=>{
    const b=blocks.get(num);if(!b)throw Error('Missing block');
    // Retain the former sixth-section fragment on its subordinate heading.
    return `${j?'<h3'+(num===6?' id="sec-6"':'')+'>'+b.heading+'</h3>':''}${b.body}`;
   }).join('\n'):(profile.extras?profile.extras[i]:profile.extra);
   return `<h2 id="sec-${i+1}">${profile.headings[i]}</h2>\n${body}`;
  }).join('\n');
  h=h.slice(0,start)+'<!-- five-section-review:2026-10-17 -->\n'+sections+'\n'+h.slice(finish);
  h=h.replace(/<nav class="toc"[\s\S]*?<\/nav>/,`<nav class="toc" aria-label="Table of contents">\n<div class="toc-title">In this article</div>\n<ol>\n${profile.headings.map((heading,i)=>`<li><a href="#sec-${i+1}">${heading}</a></li>`).join('\n')}\n<li><a href="#faq">Frequently Asked Questions</a></li>\n</ol>\n</nav>`);
  // Summary directly follows the introduction, before navigation; no TL;DR label.
  const summary=h.match(/<div class="tldr">[\s\S]*?<\/div>/);
  if(!summary)throw Error('Missing summary '+row.id);
  h=h.replace(summary[0],'');h=h.replace('<nav class="toc"',summary[0]+'\n\n<nav class="toc"');
  h=h.replace(/("dateModified"\s*:\s*")[^"]+"/g,'$12026-10-17"');
 }
 if(profile.order.flat().includes(6) && row.h2 && row.h2[5]) {
  h=h.replace('<h3>'+row.h2[5]+'</h3>','<h3 id="sec-6">'+row.h2[5]+'</h3>');
 }
 if(profile.title){
  const old=h.match(/<h1>([^<]+)<\/h1>/)[1];h=h.split(old).join(profile.title);
  for(const x of catalogue)if(x.slug===row.id)x.title=profile.title;
  for(const x of api)if(x.id===row.id)x.title=profile.title;
 }
 if(row.id==='how-sleep-debt-silently-drains-your-daily-performance'){
  const description='How sleep debt silently drains your daily performance: review sleep patterns, daytime symptoms and practical routine changes, with guidance on seeking support.';
  h=h.replace(/(<meta (?:name="description"|property="og:description") content=")[^"]*(")/g,'$1'+description+'$2');
  h=h.replace(/("description"\s*:\s*")[^"]*(")/,'$1'+description+'$2');
 }
 const description=h.match(/<meta name="description" content="([^"]+)"/)[1];
 const title=h.match(/<h1>([^<]+)<\/h1>/)[1];
 for(const item of api)if(item.id===row.id)item.shortText=description;
 for(const item of catalogue)if(item.slug===row.id)item.excerpt=description;
 homepage=homepage.replace(/<article\b[^>]*>[\s\S]*?<\/article>/g,block=>{
  if(!block.includes('/articles/'+row.id+'.html'))return block;
  block=block.replace(/(<h3><a\b[^>]*>)[^<]+/,'$1'+title).replace(/<p>[\s\S]*?<\/p>/,'<p>'+description+'</p>');
  if(row.id==='how-dopamine-actually-works-and-why-quick-fixes-backfire')block=block.replace(/alt="[^"]*"/,'alt="Woman putting her phone aside before choosing a planned guitar activity"');
  return block;
 });
 if((h.match(/<h2 id="sec-\d+">/g)||[]).length!==5)throw Error('Not five sections '+row.id);
 h=h.replace(/^[\t ]+$/gm,'');
 fs.writeFileSync(file,h);
 sitemap=sitemap.replace(/<url>[\s\S]*?<\/url>/g,b=>b.includes('/'+row.id+'.html</loc>')?b.replace(/<lastmod>[^<]+<\/lastmod>/,'<lastmod>2026-10-17</lastmod>'):b);
 console.log('Updated '+row.id);
}
fs.writeFileSync(cataloguePath,catalogueText.slice(0,catalogueText.indexOf('const ARTICLES ='))+'const ARTICLES = '+JSON.stringify(catalogue,null,2)+';\n');
fs.writeFileSync(apiPath,JSON.stringify(api,null,2)+'\n');fs.writeFileSync(path.join(root,'sitemap.xml'),sitemap);
fs.writeFileSync(path.join(root,'index.html'),homepage);
