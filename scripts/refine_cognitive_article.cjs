// Scoped editorial repair. Preserve the article shell, images, and accordion.
const fs = require('node:fs');
const file = 'articles/what-cognitive-load-does-to-your-decision-making.html';
let html = fs.readFileSync(file, 'utf8');
const paragraph = s => `<p>${s}</p>`;
const list = items => '<ul>' + items.map(s=>`<li>${s}</li>`).join('') + '</ul>';
const sections = [
 ['What Is Cognitive Load?',
 paragraph('Cognitive load describes the demands a task places on working memory, the information you are holding and using right now. A useful everyday example is comparing appointment times while someone gives you directions. Write down one set of details before comparing the other.') +
 paragraph('A crowded desk is a metaphor, not a measurement of your brain. It can help explain why keeping several details in view is useful, but it cannot tell you why you feel exhausted. Start by naming the task and the information it requires.') +
 paragraph('Research on external reminders provides a specific example of reducing reliance on memory. Gilbert\'s 2015 experiments found that reminders improved performance on a delayed-intention task. That finding does not prove that reminders cure anxiety or improve every decision; use one for a concrete thing you need to remember.') +
 list(['Write the decision in one sentence.', 'List the information you still need.', 'Keep that list visible while comparing options.', 'Separate remembering a deadline from deciding what to do.'])],
 ['How Can You Make a Complicated Decision Easier?',
 paragraph('A decision becomes easier to inspect when its criteria are visible. This is an editorial planning suggestion, not a treatment or a promise of better judgment. Try a short comparison on paper before relying on an impression of which option feels easiest.') +
 paragraph('<strong>Use three questions:</strong> What matters here, what is unknown, and when must I decide? For a course enrollment, for example, the relevant criteria might be cost, travel, and schedule. Check those facts before comparing the marketing claims.') +
 list(['Compare the same criteria for every option.', 'Mark assumptions as unknown rather than treating them as facts.', 'For a reversible, low-stakes choice, choose a reasonable option and a review date.', 'For an important financial, legal, or medical decision, obtain the relevant qualified advice.']) +
 paragraph('Feeling overwhelmed does not establish that a particular choice was wrong. Disagreement, missing information, and competing priorities can also make a decision difficult. If the feeling is familiar, our guide to <a href="../articles/why-you-feel-mentally-drained.html">understanding mental tiredness</a> offers related context; use it for reflection, not diagnosis.')],
 ['What Are the Signs You Need a Pause?',
 paragraph('Repeatedly losing your place or rereading the same options can be a practical cue to pause. These observations are not a diagnostic checklist and do not identify the cause of fatigue. Notice what changed in the task before labeling yourself as overloaded.') +
 list(['You cannot state the decision you are trying to make.', 'You keep switching between unrelated tasks.', 'Important details are scattered across several messages.', 'You are about to agree without checking the deadline or scope.']) +
 paragraph('Concentration difficulties can have several explanations. NIMH lists trouble concentrating among possible symptoms of generalized anxiety disorder, but a single difficult afternoon does not establish that diagnosis. Seek professional advice when symptoms persist or interfere with ordinary activities.') +
 paragraph('Sleep also deserves attention: NHLBI explains that sleep deficiency can affect focus and reactions. Do not assume every lapse is simply a productivity problem; note sleep and other symptoms when discussing persistent difficulties with a clinician. Our <a href="../articles/signs-of-mental-exhaustion.html">guide to recognizing mental exhaustion</a> explains additional limits.')],
 ['Why Does Mental Effort Feel Harder Sometimes?',
 paragraph('There is no universal hour when everyone makes their best decisions. Sleep, work patterns, interruptions, and the task itself differ between people. Choose a time when you personally feel reasonably alert instead of assuming that every important decision belongs before noon.') +
 paragraph('The idea that self-control draws from one steadily draining resource is not a settled explanation. A large preregistered replication by Hagger and colleagues in 2016 found an effect estimate close to zero for the tested ego-depletion procedure. This does not mean tiredness is imaginary; avoid treating the fuel-tank metaphor as established biology.') +
 list(['Check whether the problem is missing information rather than lack of effort.', 'Allow for poor sleep or an unusually demanding day.', 'Reduce interruptions for one decision instead of redesigning the whole day.', 'If a deadline cannot move, ask someone appropriate to check your reasoning.']) +
 paragraph('Workplace demands may require a workload conversation, not another personal habit. Our guide to <a href="../articles/how-to-deal-with-stress-at-work.html">discussing and managing work stress</a> can help you prepare; start with a specific request about priorities or deadlines.')],
 ['How Can You Manage Decisions Daily?',
 paragraph('A small trial can reveal whether a planning change helps you. The following worksheet is an original editorial exercise, not a validated cognitive test. Use it for one recurring, low-stakes decision and keep the effort modest.') +
 list(['Day 1: record the decision, its deadline, and what made it difficult.', 'Day 2: put the needed information in one place.', 'Day 3: add a reminder for the deadline, not for every possible action.', 'Day 4: compare how easy it was to follow the process, without scoring your intelligence.', 'Day 5: keep the helpful part and discard anything that added work.']) +
 paragraph('<strong>Example worksheet:</strong> Decision: when to shop. Criteria: opening hours, transport, and household needs. Unknown: whether someone else needs the car. Next step: ask about transport before choosing a time. Copy that structure for your own decision.') +
 paragraph('A useful default should remain easy to change. A recurring shopping time can simplify planning, but a rigid rule can create extra pressure when circumstances change. Review your default when it stops serving you.') +
 paragraph('Rest does not need to earn its place through productivity. A pause may make a task feel more manageable, but this guide cannot promise that a specific break restores a measurable reserve. See <a href="../articles/how-to-stop-feeling-guilty-for-resting.html">making room for rest without guilt</a> and choose a break that fits your circumstances.')],
 ['How Can You Respond When You Feel Overwhelmed?',
 paragraph('Start with the immediate situation rather than a theory about your brain. If it is safe to pause, stop comparing options long enough to identify what must happen next. For a routine request, a response such as “I need to check my schedule first” can create room to verify the details.') +
 list(['Write the next action, not the entire problem.', 'Ask for clarification if the request is vague.', 'Take a comfortable pause if the task allows it.', 'Return to the decision with the relevant facts in view.']) +
 paragraph('Persistent difficulty functioning deserves support, not blame. Speak with a qualified healthcare professional when concentration or fatigue disrupts daily life, or when symptoms are concerning. You do not need to wait a fixed number of weeks before asking for help.') +
 paragraph('A reflection can be useful without proving a cause. Ask what made this task harder and what practical support was missing. Choose one change to try next time rather than concluding that your judgment has run out of fuel.')]
];
for (let i=0;i<sections.length;i++) {
 const id='sec-'+(i+1), [heading,body]=sections[i];
 const re=new RegExp(`<h2 id="${id}">[\\s\\S]*?</h2>\\s*<p>[\\s\\S]*?(?=\\s*<(?:img|h2|div class="inline-promo"))`);
 if(!re.test(html)) throw new Error('Missing section '+id);
 html=html.replace(re,`<h2 id="${id}">${heading}</h2>\n${body}\n`);
 html=html.replace(new RegExp(`(<a href="#${id}">)[^<]*(</a>)`),`$1${heading}$2`);
}
html=html.replace(/(<img[^>]+loading="eager"[^>]*>[\s\S]*?)<p>What cognitive load[\s\S]*?(?=\s*<nav class="toc")/, '$1'+paragraph('What cognitive load does to your decision making can be difficult to separate from an already demanding day. If a simple choice feels unusually complicated, start by writing down the decision rather than judging yourself.')+paragraph('Difficulty choosing does not reveal a single cause. Missing information, interruptions, sleep problems, and worry can all deserve attention. Look at the situation before assuming that your mind has run out of a fixed supply of energy.')+paragraph('This guide separates a few research findings from practical planning suggestions. Use the worksheet to test a small change, and seek professional support when difficulties persist or disrupt your life.'));
html=html.replace(/(<div class="tldr">)\s*<p>[\s\S]*?<\/p>/,'$1'+paragraph('What cognitive load does to your decision making depends on the task and context; it is not evidence of a mental fuel tank running empty. Put relevant information in view, use a reminder for a specific intention, and choose a manageable time to review the options.'));
html=html.replace(/(<h2 id="real-life">[^<]*<\/h2>)\s*<p>[\s\S]*?(?=\s*<div class="author-block")/,'$1'+paragraph('Illustrative scenario: A colleague asks Alex to join a project during a busy afternoon. Alex wants to help but has not checked the deadline or current workload. Instead of agreeing immediately, Alex asks for the scope in writing and a time to respond.')+paragraph('Later, Alex compares the request with existing commitments and proposes a smaller contribution. This invented example illustrates a decision process, not proof of a psychological mechanism or a guaranteed result. Try the same pause-and-check approach on a low-stakes request.'));
const answers=[
 'It describes demands on working memory while you consider information. The outcome depends on the task and context; overload does not inevitably cause a bad choice. Write down the criteria and missing information before deciding.',
 'You may find comparison harder when information is scattered or you are repeatedly interrupted. These observations do not establish a diagnosis or a single cause. Try making the information visible and handling one question at a time.',
 'No. Cognitive load concerns task demands; decision fatigue is used to describe difficulty after repeated decisions. Neither term proves that a single mental resource has been depleted. Research on the related ego-depletion theory is contested.',
 'Reducing unnecessary demands may make a task easier to manage. Research supports reminders for some memory tasks, not every kind of decision. Test one low-stakes change and assess whether it helps you.',
 'Ask a qualified healthcare professional when difficulties persist, disrupt daily activities, or concern you. You do not need to wait a fixed period. This article cannot determine whether anxiety, sleep problems, or another condition explains your symptoms.'
];
let n=0; html=html.replace(/<div class="faq-a">[\s\S]*?<\/div>/g,()=>`<div class="faq-a">${answers[n++]}</div>`);
if(n!==5) throw new Error('Unexpected FAQ count');
html=html.replace(/(<h2[^>]*>Where to Go From Here<\/h2>)\s*<p>[\s\S]*?(?=\s*<div)/,'$1'+paragraph('You do not need a perfect routine to make a decision more manageable. Start by defining the question and putting the relevant facts in view.')+paragraph('Choose one low-stakes decision today and use the worksheet. A small experiment can show you what helps without turning every choice into another project.')+paragraph('If the difficulty continues, asking for support is a practical next step. Your experience matters even when a simple explanation does not fit.'));
html=html.replace('Source links are listed for further reading and require editorial verification before publication. They do not make this article a substitute for professional advice.','References checked on October 13, 2026 for the specific points described below. Planning exercises are editorial suggestions, not clinically validated interventions. This is not a clinical review.');
const refs=[
 ['https://pubmed.ncbi.nlm.nih.gov/25666463/','Gilbert (2015): Strategic use of reminders','Experimental evidence for reminders on a delayed-intention task; not evidence that reminders improve all decisions.'],
 ['https://www.psychologicalscience.org/journals/perspectives/1745691616652873/','Hagger et al. (2016): A Multilab Preregistered Replication of the Ego-Depletion Effect','Evidence limiting confidence in the tested depletion effect, not a claim that mental fatigue does not exist.'],
 ['https://www.nhlbi.nih.gov/health/sleep-deprivation','NHLBI: Sleep Deprivation and Deficiency','Sleep deficiency can affect focus and reactions; this does not establish the cause of an individual reader\'s symptoms.'],
 ['https://www.nimh.nih.gov/health/publications/generalized-anxiety-disorder-gad','NIMH: Generalized Anxiety Disorder','Concentration difficulties can occur with GAD; diagnosis requires professional assessment.']
];
const marker=html.indexOf('Sources &amp; References');
const before=html.slice(0,marker), after=html.slice(marker).replace(/<ul[^>]*>[\s\S]*?<\/ul>/,'<ul>'+refs.map(([url,title,note])=>`<li><a href="${url}" target="_blank" rel="noopener">${title}</a>: ${note}</li>`).join('\n')+'</ul>');
html=before+after;
html=html.replaceAll('7 Things What Cognitive Load Does to Your Decision Making (And How to Finally Think Clearly)','What Cognitive Load Does to Your Decision Making: 5 Practical Checks');
html=html.replaceAll('Discover what cognitive load does to your decision making, why mental overload causes poor choices, and simple steps to think more clearly every day. Read on.','Learn what cognitive load does to your decision making, with practical checks, clear research limits, and a simple worksheet to help you compare everyday choices.');
html=html.replace('"dateModified": "2026-10-12"','"dateModified": "2026-10-13"');
if(html.includes('make it before noon') || html.includes('same limited pool')) throw new Error('Stale claim');
html=html.replaceAll('a simple worksheet to help you compare everyday choices.', 'a simple worksheet to help compare everyday choices.');
fs.writeFileSync(file,html);
const oldTitle='7 Things What Cognitive Load Does to Your Decision Making (And How to Finally Think Clearly)';
const title='What Cognitive Load Does to Your Decision Making: 5 Practical Checks';
for(const p of ['index.html','articles.js','api/articles.json']) {
 if(!fs.existsSync(p)) continue;
 const value=fs.readFileSync(p,'utf8').replaceAll(oldTitle,title).replaceAll('What cognitive load does to your decision making is something most people never connect to the poor choices they make on hard days. You snap at someone...', 'Compare everyday choices with a practical worksheet, specific research findings, and clear limits on claims about mental energy.');
 fs.writeFileSync(p,value);
}
const meta=html.match(/name="description" content="([^"]+)"/)[1];
if(meta.length<155 || meta.length>160) throw new Error('Meta length '+meta.length);
if((html.match(/class="faq-a"/g)||[]).length!==5 || (html.match(/<img /g)||[]).length!==4) throw new Error('Layout regression');
for(const [,json] of html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)) JSON.parse(json);
console.log('PASS: four images, five FAQ answers, valid structured data, meta length '+meta.length);
