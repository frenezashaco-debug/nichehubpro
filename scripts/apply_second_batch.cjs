const fs = require('node:fs');
const path = require('node:path');
const {data, S, p, ul, link, src} = require('./second_batch_content.cjs');
const root = path.resolve(__dirname, '..');
const escape = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const plain = s => s.replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim();
const outputs = new Map();
function get(slug) { return fs.readFileSync(path.join(root, 'articles', slug+'.html'), 'utf8'); }
function once(h, re, replacement) { const matches = [...h.matchAll(new RegExp(re.source, 'g'))]; if(matches.length !== 1) throw Error('Expected one match: '+re+' got '+matches.length); return h.replace(re, replacement); }
function divContaining(h, marker) {
 const at = h.indexOf(marker); if(at<0) return null;
 const stack=[]; const re=/<\/?div\b[^>]*>/g; let m;
 while((m=re.exec(h)) && m.index<at) { if(m[0].startsWith('</')) stack.pop(); else stack.push(m.index); }
 const start=stack.at(-1); if(start===undefined) throw Error('No containing div '+marker);
 let depth=0; re.lastIndex=start;
 while((m=re.exec(h))) { depth += m[0].startsWith('</') ? -1 : 1; if(depth===0) return [start,re.lastIndex]; }
 throw Error('Unclosed div');
}
function replaceDiv(h, marker, content) { const range=divContaining(h,marker); if(!range) throw Error('Missing '+marker); return h.slice(0,range[0])+content+h.slice(range[1]); }
function intro(h, paragraphs) { return once(h, /(<article class="article-content" id="article-body">)\s*(?:<p>[\s\S]*?<\/p>\s*)+/, '$1\n'+p(...paragraphs)+'\n'); }
function example(h, paragraphs) { return once(h, /(<h2[^>]*>An Illustrative Scenario<\/h2>)\s*(?:<p>[\s\S]*?<\/p>\s*)+/, '$1\n'+p(...paragraphs)+'\n'); }
function conclusion(h, paragraphs) { return once(h, /(<h2>Where to Go From Here<\/h2>)\s*(?:<p>[\s\S]*?<\/p>\s*)+/, '$1\n'+p(...paragraphs)+'\n'); }
function summary(h, text) { return once(h, /<div class="tldr">[\s\S]*?<\/div>/, '<div class="tldr">'+p(text)+'</div>'); }
function paragraph(h, prefix, text) { return once(h, new RegExp('<p>'+escape(prefix)+'[\\s\\S]*?<\\/p>'), p(text)); }
function faq(h, questions) {
 const range=divContaining(h, '<h2>Frequently Asked Questions</h2>'); if(!range) throw Error('FAQ missing');
 const markup='<div class="faq-section" id="faq"><h2>Frequently Asked Questions</h2>'+questions.map(([q,a])=>`<div class="faq-item"><button class="faq-q">${q}<span class="faq-icon">+</span></button><div class="faq-a">${a}</div></div>`).join('\n')+'</div>';
 return h.slice(0,range[0])+markup+h.slice(range[1]);
}
function finalize(slug,h,d) {
 const oldTitle=plain(h.match(/<h1[^>]*>([\s\S]*?)<\/h1>/)[1]);
 if(d.title) h=h.replaceAll(oldTitle,d.title);
 if(d.description) {
  // Descriptions are authored, never padded or truncated mechanically.
  if(d.description.length<155||d.description.length>160) throw Error(slug+' meta length '+d.description.length);
  h=h.replace(/(<meta (?:name="description"|property="og:description"|name="twitter:description") content=")[^"]*("[^>]*>)/g, '$1'+d.description+'$2');
 }
 if(d.faq) h=faq(h,d.faq);
 if(d.conclusion) h=conclusion(h,d.conclusion);
 // Replace broad boilerplate reference boxes with topic-specific sources.
 for(const marker of ['Sources &amp; References','Evidence-based references']) {
  while(h.includes(marker)) h=replaceDiv(h,marker,'');
 }
 const refs='<div class="sources-card"><h3>Sources and scope</h3>'+p('These sources support the general guidance identified in the text. Planning worksheets and fictional examples are editorial tools, not tested treatments.')+ul(...d.sources.map(k=>src(...S[k])))+'</div>\n';
 const disclaimer=h.indexOf('This article is for informational purposes only');
 if(disclaimer<0) throw Error('Disclaimer missing');
 const range=divContaining(h,'This article is for informational purposes only');
 h=h.slice(0,range[0])+refs+h.slice(range[0]);
 const faqs=d.faq||[...h.matchAll(/<button class="faq-q">([\s\S]*?)<span class="faq-icon">[\s\S]*?<div class="faq-a">([\s\S]*?)<\/div>/g)].map(m=>[plain(m[1]),plain(m[2])]);
 if(faqs.length!==5) throw Error(slug+' expected five FAQs');
 let hadFAQ=false;
 h=h.replace(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g,(tag,json)=>{
  const obj=JSON.parse(json);
  function visit(x){if(!x||typeof x!=='object')return;
   if(x['@type']==='Article'||x['@type']==='BlogPosting'){x.dateModified='2026-10-15';if(d.title)x.headline=d.title;if(d.description)x.description=d.description;}
   if(x['@type']==='FAQPage'){hadFAQ=true;x.mainEntity=faqs.map(([q,a])=>({'@type':'Question',name:q,acceptedAnswer:{'@type':'Answer',text:a}}));}
   Object.values(x).forEach(v=>{if(Array.isArray(v))v.forEach(visit);else if(v&&typeof v==='object')visit(v);});
  }visit(obj);return '<script type="application/ld+json">'+JSON.stringify(obj)+'</script>';
 });
 if(!hadFAQ) h=h.replace('</head>','<script type="application/ld+json">'+JSON.stringify({'@context':'https://schema.org','@type':'FAQPage',mainEntity:faqs.map(([q,a])=>({'@type':'Question',name:q,acceptedAnswer:{'@type':'Answer',text:a}}))})+'</script>\n</head>');
 const words=plain(h.slice(h.indexOf('<article class='),h.indexOf('</article>'))).split(/\s+/).length;
 h=h.replace(/(<span id="read-time">)\d+(<\/span>)/,'$1'+Math.ceil(words/220)+'$2');
 if((h.match(/<img\b/g)||[]).length!==4) throw Error(slug+' image count');
 if((h.match(/class="faq-a"/g)||[]).length!==5) throw Error(slug+' FAQ count');
 if(/—|TL;DR:|Images in this article are AI-generated illustrations\./.test(h)) throw Error(slug+' prohibited label or punctuation');
 outputs.set(slug,h);
}
for(const [slug,d] of Object.entries(data)) {
 let h=get(slug);
 const re=/<article class="article-content" id="article-body">[\s\S]*?<h2[^>]*>An Illustrative Scenario<\/h2>\s*(?:<p>[\s\S]*?<\/p>\s*)+/;
 const old=h.match(re)?.[0]; if(!old)throw Error(slug+' body missing');
 const images=old.match(/<img\b[^>]*>/g);let cover='';if(images?.length===4)cover=images.shift();if(images?.length!==3)throw Error(slug+' inline images');
 const promo=old.match(/<div class="inline-promo">[\s\S]*?<\/a>\s*<\/div>/)?.[0]||'';
 const toc='<nav class="toc" aria-label="Table of contents"><div class="toc-title">In this article</div><ol>'+d.sections.map(([title],i)=>`<li><a href="#sec-${i+1}">${title}</a></li>`).join('')+'<li><a href="#faq">Frequently Asked Questions</a></li></ol></nav>';
 let b='<article class="article-content" id="article-body">\n'+cover+p(...d.intro)+'<div class="tldr">'+p(d.summary)+'</div>'+toc;
 d.sections.forEach(([title,content],i)=>{b+=`<h2 id="sec-${i+1}">${title}</h2>`+content;if(i===0)b+=images[0];if(i===1)b+=promo;if(i===2)b+=images[1];if(i===4)b+=images[2];});
 b+='<h2 id="real-life">An Illustrative Scenario</h2>'+p(...d.example)+'\n';
 h=once(h,re,b); finalize(slug,h,d);
}

// Targeted revisions retain already-cautious sections, while repairing contradictions.
{
 const slug='foods-that-reduce-anxiety';let h=get(slug);
 h=intro(h,['Foods that reduce anxiety is a common search, but no shopping list can promise relief from an anxiety disorder. Start with food that fits your needs rather than a claim about changing brain chemicals.', 'Stress can make shopping and meal preparation harder. A practical backup meal may solve an access problem even when it does not change anxiety symptoms.', 'This guide offers seven food options, a flexible planning method, and questions for qualified support. Use it alongside care, not instead of it.']);
 h=summary(h,'Foods that reduce anxiety should be understood as nutritious options, not proven anxiety treatments. Choose varied meals you tolerate and can afford, and seek qualified help when anxiety interferes with daily life.');
 h=h.replaceAll('Why Do These Foods Reduce Anxiety Specifically?', 'Why Is Food Only One Part of Anxiety Care?');
 h=h.replaceAll('What Are the 7 Best Foods That Reduce Anxiety?', 'What Are 7 Food Options to Consider Without Treatment Promises?');
 h=paragraph(h,'Food can support general health,', `Food can support ordinary meals and routines without treating an anxiety disorder. ${src(...S.food)} describes a varied eating pattern, while ${src(...S.anxiety)} describes professional anxiety care; use each source for its own purpose.`);
 h=h.replace('<h2>An Illustrative Scenario</h2>', '<h3>A backup-meal card</h3>'+p('Write one familiar meal, its available substitute, and the barrier that makes preparation difficult. This card is a planning aid, not an anxiety score.')+ul('Usual meal: a sandwich with a filling you enjoy.', 'Fallback: an affordable ready-to-eat option safe for your dietary needs.', 'Barrier: no break, missing ingredients, or difficult preparation.', 'Next step: arrange access or help rather than restricting another food.')+p(`For other parts of the day, consider ${link('how-to-deal-with-anxiety-daily','planning daily anxiety support')}, ${link('how-to-sleep-better-naturally','sleep habits and their limits')}, and ${link('healthy-habits-for-busy-people','meal access during busy weeks')}.`)+ '<h2>An Illustrative Scenario</h2>');
 finalize(slug,h,{
 title:'Foods That Reduce Anxiety: 7 Options Without Cure Claims',
 description:'Explore foods that reduce anxiety as part of balanced eating, not a cure: seven flexible options, a backup-meal card, and guidance on seeking qualified support.',
 sources:['food','anxiety'],
 faq:[['Can food cure an anxiety disorder?','No specific food in this guide is a proven cure. Nutrition can support general wellbeing, while anxiety that affects daily life deserves qualified care.'],['Which foods should I start with?','Choose a familiar meal and add an affordable option you tolerate, such as fruit, vegetables, beans, or whole grains. Adapt choices for allergies and medical advice.'],['Should I take magnesium or other supplements?','Do not infer a deficiency from anxiety symptoms. Ask a qualified professional whether a supplement is appropriate, especially if you take medicines.'],['Do I have to eat fermented foods?','No. They are optional, and not everyone tolerates them. A varied pattern does not depend on one ingredient.'],['What if planning meals increases my anxiety?','Simplify the plan and seek support, especially if you become restrictive or food choices cause distress. A dietitian or appropriate clinician can help personalize advice.']]
 });
}
{
 const slug='natural-energy-boosters';let h=get(slug);
 h=paragraph(h,'<strong>Your action:</strong> Choose one habit', 'Your action: choose one practical obstacle to address, such as no access to a meal break. Record whether the change was feasible; a self-rating is not a diagnostic test.');
 h=h.replace('The log helps them see that several busy days and late caffeine are affecting their routine.', 'The log records busy days and caffeine timing without establishing which factor, if any, caused the fatigue.');
 h=h.replace('A clinician can help assess symptoms that self-care cannot explain.', `A clinician can help assess symptoms that self-care cannot explain. ${src(...S.fatigue)} describes possible causes and reasons to seek care; do not wait for the two-week experiment if symptoms are concerning.`);
 h=h.replace('<h2>An Illustrative Scenario</h2>', '<h3>Choose by the obstacle, not the product</h3>'+p('Before adding a habit, match the next step to what is missing. This is an organizational check, not a diagnosis.')+ul('No time for lunch: protect a meal opportunity or arrange a suitable backup.', 'No opportunity for sleep: identify work or care responsibilities that need support.', 'Activity makes symptoms worse: stop pushing through and discuss the pattern with a clinician.', 'No clear explanation: arrange assessment rather than adding supplements.')+p(`Use ${link('how-to-increase-energy-naturally','a fatigue appointment worksheet')}, ${link('how-to-sleep-better-naturally','sleep planning checks')}, and ${link('healthy-habits-for-busy-people','a fallback routine for difficult weeks')} for different planning needs.`)+ '<h2>An Illustrative Scenario</h2>');
 finalize(slug,h,{title:'Natural Energy Boosters: 7 Options With Realistic Limits',description:'Compare natural energy boosters with seven realistic options, an obstacle-based planning checklist, and advice on when tiredness needs professional attention.',sources:['fatigue','sleep','food'],faq:[['What is a natural energy booster?','Here it means an everyday habit such as protecting sleep or meal access, not a product or treatment for fatigue.'],['Should I try all seven options?','No. Choose one that addresses a practical obstacle, and avoid delaying care for unexplained symptoms.'],['Can I track energy with a number?','You can describe your experience that way, but a personal rating is not a diagnostic test. Concrete examples of difficult activities can also help an appointment.'],['What if movement makes me feel worse?','Do not push through symptoms. Record any immediate or delayed worsening and discuss it with a qualified clinician.'],['Are supplements safer because they are natural?','Natural does not mean safe or necessary. Ask a clinician or pharmacist before using supplements, particularly alongside medicines.']]});
}
{
 const slug='why-hydration-affects-your-focus-more-than-you-think';let h=get(slug);
 h=example(h,['Illustrative example: a project coordinator notices they rarely have a drink available during long meetings. They put water within reach and ask for a short break between calls.', 'The change improves access to fluids, but the example does not establish better concentration or a medical cause of tiredness. Persistent symptoms still need assessment, and any prescribed fluid limit takes priority.']);
 h=h.replace('On hot or active days, plan ahead and follow public-health advice to drink more fluids.', 'On hot or active days, plan ahead for fluid needs. If you have a prescribed fluid limit, ask your care team how to adapt rather than increasing intake yourself.');
 h=h.replace('<h2 id="real-life">An Illustrative Scenario</h2>', '<h3>A meeting-day access check</h3>'+p('Check access before setting a drinking target. The aim is to remove a barrier, not to measure your concentration through bottle volume.')+ul('Can you reach a drink during the meeting?', 'Can you pause for a bathroom break?', 'Does heat or illness change the situation?', 'Do you have a prescribed fluid limit to follow?')+p(`Pair this with ${link('how-to-increase-energy-naturally','assessing ongoing tiredness')}, ${link('healthy-habits-for-busy-people','planning breaks in a busy schedule')}, and ${link('how-to-sleep-better-naturally','reviewing sleep opportunities')}; water is not the only factor to consider.`)+'<h2 id="real-life">An Illustrative Scenario</h2>');
 finalize(slug,h,{title:'Why Hydration Affects Your Focus More Than You Think: 5 Practical Checks',description:'Learn why hydration affects your focus more than you think, with practical access checks, individual fluid limits, and warning signs that need medical advice.',sources:['water','dehydration'],conclusion:['Start with access rather than a promise of sharper thinking. Put a suitable drink where you can reach it, following any medical limits.','Notice persistent symptoms without deciding that water must explain them. A useful habit does not rule out other causes.','Choose one practical improvement today, such as a break between meetings. Seek appropriate care when symptoms are concerning rather than waiting for a bottle to solve them.']});
}
{
 const slug='how-to-build-energy-that-lasts-all-day-without-crashing';let h=get(slug);
 h=paragraph(h,'The NIDDK also points out', `${src(...S.habits)} describes planning and reviewing health habits. That supports using a manageable experiment, not a claim that small changes reliably cure afternoon fatigue.`);
 h=paragraph(h,'Dehydration is easy to overlook too.', 'Fluid access is one practical factor to review, but a tired afternoon does not establish dehydration. Keep an appropriate drink available and follow any prescribed fluid limits.');
 h=paragraph(h,'Start with the habit that feels most achievable right now.', 'One useful change might be protecting time for a meal. Review whether it removed an obstacle without assuming it caused a medical improvement.');
 h=paragraph(h,'Start with light before caffeine if you can.', 'Plan a morning that is feasible rather than a prescribed order of actions. Daytime outdoor time may fit your routine, but there is no requirement here to get light before drinking coffee.');
 h=paragraph(h,'Drink water before your first coffee.', 'Keep fluids accessible when convenient. There is no requirement to drink a fixed amount before coffee, and prescribed fluid restrictions take priority.');
 h=h.replaceAll('Hydrate before caffeinating','Make appropriate fluids accessible');
 h=h.replace('Reduce your caffeine after midday.', 'Review caffeine timing.');
 h=h.replace('The good news is it is often fixable with a few targeted changes.', 'Routine adjustments may help some people, but persistent or unexplained fatigue deserves assessment.');
 h=h.replace('<h2 id="real-life">An Illustrative Scenario</h2>', '<h3>An afternoon decision note</h3>'+p('Use three lines to separate a practical obstacle from an unexplained symptom. This is a planning aid, not a diagnostic instrument.')+ul('What is missing right now: rest, meal access, a break, or something unclear?', 'What can change safely today: one task, one arrangement, or a request for help?', 'What needs follow-up: recurring fatigue, worsening symptoms, or a medical-care question?')+p(`For the follow-up note, use ${link('how-to-increase-energy-naturally','recording fatigue for an appointment')}, ${link('natural-energy-boosters','choosing a realistic energy habit')}, and ${link('why-hydration-affects-your-focus-more-than-you-think','fluid guidance without fixed targets')}.`)+ '<h2 id="real-life">An Illustrative Scenario</h2>');
 finalize(slug,h,{title:'How to Build Energy That Lasts All Day Without Crashing: 7 Realistic Checks',description:'Review how to build energy that lasts all day without crashing with seven realistic checks, an afternoon decision note, and limits on what habits can explain.',sources:['fatigue','sleep','habits','food'],faq:[['Does an afternoon slump mean low blood sugar?','No. Timing and tiredness alone cannot establish that. If you have diabetes or a glucose-care plan, follow your care team\'s instructions.'],['Can I guarantee steady energy all day?','No. Needs and symptoms vary. Review practical barriers without promising yourself constant alertness.'],['Should I drink water before coffee?','There is no required order in this guide. Keep fluids accessible and follow prescribed limits; water is not a substitute for assessing persistent fatigue.'],['What if a break does not help?','A break cannot address every cause. Seek advice when fatigue persists, worsens, or affects daily life, rather than adding increasingly strict routines.'],['What should I record before an appointment?','Note when symptoms began, the tasks affected, sleep and medicine context, and any worsening after exertion. Concrete examples can help explain the problem.']]});
}
// Validate the entire batch before writing any article.
for(const [slug,h] of outputs) {
 for(const match of h.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g))JSON.parse(match[1]);
 if(!h.includes('This article is for informational purposes only and does not replace professional medical advice.'))throw Error(slug+' disclaimer');
}
for(const [slug,h] of outputs) fs.writeFileSync(path.join(root,'articles',slug+'.html'),h);
console.log('Updated '+outputs.size+' articles; preserved four images per article and synchronized five FAQs.');
