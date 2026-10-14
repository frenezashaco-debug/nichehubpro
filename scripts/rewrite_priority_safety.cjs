const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const p=s=>`<p>${s}</p>`;
const ul=items=>'<ul>'+items.map(s=>`<li>${s}</li>`).join('')+'</ul>';
const datasets={
'how-to-stop-panic-attacks':{
intro:[
'How to stop panic attacks can feel like an urgent question when your heart races or breathing feels difficult. This page cannot determine whether your symptoms are panic. Start with safety rather than assuming a familiar label explains a new episode.',
'New, severe, or unusual symptoms need medical attention. For sudden chest pain that does not go away, especially with breathlessness, sweating, or feeling faint, seek emergency help through your local emergency service. Do not delay help to complete an exercise.',
'If a clinician has assessed similar episodes and helped you make a plan, use that plan. The five practical steps below help organize a response and prepare for follow-up; none guarantees that an attack will stop.'],
summary:'How to stop panic attacks does not have one reliable instant method. Check whether medical help is needed, use your agreed care plan, and consider a comfortable coping step if appropriate. Recurring episodes deserve professional assessment rather than an increasingly strict self-help routine.',
sections:[
['What is a panic attack?',[
'A panic attack is an episode of intense fear or discomfort that may include physical symptoms. It is not the same as a diagnosis of panic disorder. Use the description to explain your experience to a clinician, not to rule out another condition.',
'An episode can occur without an obvious trigger. Failing to identify a cause does not mean that you caused the attack or ignored a warning. Describe what happened without inventing a neurological explanation.'],['Note when the symptoms began.','Describe what you felt in your own words.','Mention whether this episode differs from previous ones.']],
['What are the signs, and when is urgent help needed?',[
'Racing heart, trembling, nausea, and feeling detached can occur with panic, but symptoms can overlap with physical illness. A symptom list cannot tell you that your heart or breathing is safe. Seek medical assessment for new or concerning symptoms.',
'A previous reassuring examination does not explain every future episode. If symptoms change, follow appropriate medical advice instead of automatically repeating a coping exercise. Ask your clinician what should prompt urgent help in your particular situation.'],['Do not wait for a fixed symptom count before seeking help.','Do not use a timer to decide whether chest symptoms are serious.','If you feel unsafe where you are, move to safety or ask for assistance.']],
['Why does panic happen?',[
'Panic does not have one explanation that applies to every person. The NIMH describes unexpected attacks and several possible contributing processes. Discuss your health history and circumstances with a professional rather than assuming one habit caused the problem.',
'Worry about another episode may affect daily activities. If you are avoiding travel, work, or social plans, describe those changes at an appointment. An individualized treatment plan is more useful than a promise to prevent every attack.'],['Bring a list of medicines and supplements to an assessment.','Mention changes in sleep and substance use without assuming causation.','Describe activities you have stopped or restricted.']],
['How can you respond? Five practical steps',[
'<strong>1. Check safety first.</strong> Consider whether symptoms are new, severe, or different and whether you need medical help. An online reassurance cannot replace that decision.',
'<strong>2. Use your agreed plan.</strong> If you have a clinician-provided plan for assessed episodes, keep it accessible. Avoid adding multiple unfamiliar techniques while distressed.',
'<strong>3. Try gentle breathing only if comfortable.</strong> NHS guidance describes breathing gently without forcing it. There is no need here for breath-holding, maximal breaths, or continuing until a measured heart rate falls. Stop if the exercise makes you feel worse.',
'<strong>4. Choose an external point of attention if useful.</strong> You might describe the room or feel the support of your chair. This is an optional coping suggestion, not proof that your symptoms are harmless.',
'<strong>5. Ask for appropriate support.</strong> A trusted person can help you contact care or follow your existing plan. Ask for a concrete action rather than relying on repeated reassurance that nothing is wrong.'],['Choose one tolerable step, not a performance checklist.','Do not submerge your face in cold water as an emergency substitute for care.','Do not remain in an unsafe situation to avoid being seen as avoidant.']],
['How can you manage recurring panic day to day?',[
'Recurring panic can be treated with professional support. NIMH describes psychotherapy, medication, or both, chosen for the individual. Arrange an assessment rather than judging yourself by whether breathing exercises are enough.',
'<strong>Prepare a short appointment note:</strong> when an episode happened, what symptoms occurred, what was different, and what activities it affected. This original organizational prompt is not a diagnostic test. Stop detailed tracking if it becomes repeated checking.',
'Daily routines may support ordinary life, but no morning ritual prevents all attacks. Use our guide to <a href="/articles/how-to-deal-with-anxiety-daily.html">daily coping with anxiety</a> for context, and discuss persistent problems with a professional.',
'Sleep and workload are useful topics to raise without treating them as the whole explanation. Our guides to <a href="/articles/anxiety-before-sleep.html">worry around bedtime</a> and <a href="/articles/how-to-set-healthy-boundaries.html">setting manageable boundaries</a> offer related planning ideas; adapt them to your care plan.'],['Write down questions before an appointment.','Ask how to respond if symptoms change.','Do not change prescribed medication without professional advice.']]],
example:['<strong>Invented planning example:</strong> Alex has previously discussed panic with a clinician. Before travelling, Alex saves the agreed plan and asks a companion how they can help contact care if needed.','During a later episode, Alex notices that the symptoms are different from the ones previously assessed and seeks medical advice rather than assuming they are panic. This example illustrates a decision, not a reported treatment outcome.'],
faq:[
'No coping method is reliably fastest for everyone. If symptoms are new or concerning, prioritize assessment. For episodes already assessed, follow your individual plan and choose a comfortable coping step.',
'Panic symptoms can resemble other conditions. This page cannot establish that your symptoms are harmless. New, severe, or different symptoms warrant medical attention; urgent symptoms should not be managed only with an exercise.',
'There may be several contributing factors, and attacks can be unexpected. A clinician can assess recurring episodes and their effect on daily life. You do not have to discover a trigger before seeking care.',
'Duration varies and does not by itself identify the cause. Do not wait for a particular number of minutes before seeking help for concerning symptoms.',
'Check immediate safety, seek appropriate medical help when needed, and use your existing care plan if you have one. A trusted person can help you contact support. Avoid forcing breathing or using cold-water immersion as an emergency remedy.'],
conclusion:['You do not need to master a technique before asking for help. Your symptoms and their impact deserve attention.','Choose one useful preparation today, such as writing a question for your clinician or saving an existing care plan somewhere accessible.','Progress is not a promise that panic will never return. Appropriate support and a clear response plan can be more useful than demanding perfect control.'],
sources:[['https://www.nimh.nih.gov/health/publications/panic-disorder-when-fear-overwhelms','NIMH: Panic Disorder','Unexpected attacks, assessment, and individualized treatment options.'],['https://www.nhs.uk/mental-health/self-help/guides-tools-and-activities/breathing-exercises-for-stress/','NHS: Breathing exercises for stress','Gentle, comfortable breathing without forcing the breath.'],['https://www.nhs.uk/symptoms/chest-pain/','NHS: Chest pain','Reasons to seek urgent care rather than assume chest symptoms are anxiety.']]
},
'morning-routine-for-a-healthy-lifestyle':{
intro:['A morning routine for a healthy lifestyle should fit the morning you actually have. Work, caregiving, disability, and shift schedules can leave little room for an idealized checklist. Start with one practical difficulty rather than a complete makeover.','A rushed start does not prove that your hormones or nervous system need resetting. A missing lunch or an unrealistic departure time may be the more useful problem to solve. Name that problem before adding another habit.','This guide offers a flexible planning method and a fallback example. It is not a treatment for fatigue, anxiety, or blood sugar problems. Seek professional advice when symptoms persist or interfere with daily life.'],
summary:'A morning routine for a healthy lifestyle can start with one action that supports your actual needs. Protect sleep, allow for food and medicines as appropriate, and prepare a fallback for busy days. No fixed sequence, nutrient target, or 30-day plan guarantees better health.',
sections:[
['What is a healthy morning routine?',[
'A morning routine is simply a sequence of activities around the start of your day. Its usefulness depends on your responsibilities and needs, not whether it takes place before a particular hour. Define what the routine is meant to make easier.',
'Enough sleep matters more than squeezing in an elaborate checklist. NHLBI recommends making time for sleep and maintaining a reasonably consistent schedule where possible. Do not set an earlier alarm merely to copy someone else.'],['Identify the first necessary task.','Allow time for prescribed care or accessibility needs.','Treat optional habits as optional.']],
['What are the signs your plan needs adjusting?',[
'A practical mismatch shows up in repeated obstacles: leaving without something essential, skipping a necessary task, or running out of time. Notice which part of the sequence breaks down rather than scoring yourself against a wellness list.',
'Persistent tiredness, anxiety, or other symptoms are not proof of a bad morning routine. Record their effect on your day and seek an assessment when needed. A checklist cannot diagnose the cause.'],['Does the plan require time you do not have?','Does it depend on someone else being available?','Does it reduce sleep or create pressure?']],
['Why can a routine be difficult to maintain?',[
'Plans often assume an ordinary day with no interruptions. A late bus or a child needing help can make the full version impossible. Decide what you can omit without losing the essential purpose.',
'A reminder may help you remember an action, but it does not guarantee automatic behavior. Place an item where you will use it and see whether the arrangement helps. Our <a href="../articles/how-to-create-sustainable-healthy-habits.html">guide to sustainable habit planning</a> discusses adapting the action.'],['Distinguish essentials from preferences.','Choose a cue you usually encounter.','Keep a version that works when time is short.']],
['How can you build a routine that fits?',[
'<strong>Step 1: Choose one obstacle.</strong> For example, preparing lunch may take longer than you expect. Write down what makes it difficult: ingredients, storage, timing, or a decision about what to eat.',
'<strong>Step 2: Move one decision earlier.</strong> You might choose lunch the night before while keeping it stored safely. This is a planning suggestion, not a promise to improve energy or hormone levels.',
'<strong>Step 3: Define a fallback.</strong> If the preferred meal is unavailable, decide what accessible alternative fits your needs. Follow individualized dietary advice for a medical condition rather than a universal protein target.',
'<strong>Step 4: Review the practical outcome.</strong> Ask whether you left with what you needed and whether preparation cost too much time. Keep or change the plan based on that answer, not a fixed deadline for habit formation.'],['Obstacle: what is repeatedly difficult?','Normal plan: what would help on an ordinary day?','Fallback: what is the smallest useful alternative?','Review: did it solve the original problem?']],
['How can you manage the routine daily?',[
'Food and fluids should fit your health needs, access, and preferences. No breakfast can promise six hours of stable blood sugar or eliminate anxiety. Ask a qualified professional for individualized advice when needed.',
'Daylight and movement can be part of an ordinary day, not a compulsory early-morning treatment. If you spend time outdoors, use appropriate sun and eye protection. Do not stare at the sun or remove sunglasses to meet a wellness rule.',
'The National Eye Institute recommends sunglasses that protect against UVA and UVB. Light therapy is a separate intervention, not an automatic replacement for daylight; discuss it with a healthcare professional when relevant.',
'Consider how the routine fits your whole schedule. Our guides to <a href="../articles/how-to-sleep-better-naturally.html">supporting sleep habits</a> and <a href="../articles/healthy-habits-for-busy-people.html">manageable habits on busy days</a> offer related ideas. Choose what addresses your needs rather than adding every suggestion.'],['Keep necessary medicines and care in the plan.','Leave room for assistance, transport, and caregiving.','Review optional steps when circumstances change.']]],
example:['<strong>Invented planning example:</strong> Sam works an early shift and keeps leaving lunch behind. Rather than waking earlier for a long routine, Sam puts a reminder beside the keys and prepares a suitable meal the evening before.','On a day when preparation is not possible, Sam uses a preselected alternative. The example illustrates a fallback, not an observed change in fatigue, anxiety, or blood sugar. Choose an equally specific problem for your own plan.'],
faq:['There is no single best routine. Choose one action that meets your needs without reducing sleep or interfering with necessary care. Expand only if it remains useful.','There is no required duration. A short preparation step can be enough for a specific problem. Judge the routine by usefulness, not the number of minutes.','Choose a time that fits your obligations and allows adequate sleep. Shift work or sleep difficulties may need individualized advice; waking earlier is not automatically healthier.','A routine can organize necessary tasks, but it cannot guarantee better health or treat persistent symptoms. Compare its practical benefit with its time and effort cost.','Start with what you need, such as prescribed care, getting ready, or breakfast if appropriate. Drinking water before everything else is not a universal health requirement; follow individual fluid advice when applicable.'],
conclusion:['Your morning does not need to resemble a wellness demonstration. A useful plan serves your needs and can change when those needs change.','Choose one obstacle today and write a normal plan plus a fallback. That is enough for a first experiment.','If symptoms continue, ask for support rather than adding more habits. A routine is a tool, not a measure of your worth.'],
sources:[['https://www.nhlbi.nih.gov/health/sleep-deprivation/healthy-sleep-habits','NHLBI: Healthy Sleep Habits','Protecting time for sleep and adapting schedules, including shift work.'],['https://www.nei.nih.gov/eye-health-information/healthy-vision/how-eyes-work/keep-your-eyes-healthy','National Eye Institute: Keep Your Eyes Healthy','Protecting eyes outdoors with suitable sunglasses.'],['https://www.nimh.nih.gov/health/topics/caring-for-your-mental-health','NIMH: Caring for Your Mental Health','General self-care and seeking help when difficulties persist.']]
}}
for(const [slug,d]of Object.entries(datasets)){
 const file=path.join(root,'articles',slug+'.html');let html=fs.readFileSync(file,'utf8');
 const match=html.match(/(<article\b[^>]*>)([\s\S]*?)(<\/article>)/i);if(!match)throw Error('Missing article');
 const original=match[2];const author=original.indexOf('<div class="author-block');if(author<0)throw Error('Missing author');
 const images=[...original.matchAll(/<img\b[^>]*>/gi)].map(m=>m[0]);
 let tail=original.slice(author).replace(/<img\b[^>]*>/gi,'');
 let i=0;tail=tail.replace(/(<div class="faq-a">)[\s\S]*?<\/div>/g,(_,start)=>start+d.faq[i++]+'</div>');if(i!==5)throw Error('FAQ count');
 tail=tail.replace(/(<h2>Where to Go From Here<\/h2>)[\s\S]*?(?=\s*<div)/,'$1'+d.conclusion.map(p).join(''));
 const sources='<div class="sources-box"><h2>Sources &amp; References</h2>'+p('These sources support the specific points named below. Planning examples and worksheets are editorial suggestions, not clinical tests or reported outcomes.')+ul(d.sources.map(([url,label,scope])=>`<a href="${url}" target="_blank" rel="noopener">${label}</a>: ${scope}`))+'</div>';
 // Remove obsolete reference panels instead of retaining contradictory attribution.
 tail=tail.replace(/<div[^>]*>\s*<p[^>]*>Sources &amp; References<\/p>[\s\S]*?<\/ul>\s*<\/div>/, '');
 tail=tail.replace(/<section[^>]*>\s*<h[23][^>]*>Evidence-based references<\/h[23]>[\s\S]*?<\/section>/, '');
 let body=d.intro.map(p).join('')+'<div class="tldr">'+p(d.summary)+'</div>';
 body+='<nav class="toc" aria-label="Table of contents"><div class="toc-title">In this article</div><ol>'+d.sections.map(([heading],n)=>`<li><a href="#sec-${n+1}">${heading}</a></li>`).join('')+'</ol></nav>';
 let imageIndex=0;
 body+=d.sections.map(([heading,paras,items],n)=>`<h2 id="sec-${n+1}">${heading}</h2>`+paras.map(p).join('')+ul(items)+(n<images.length?images[imageIndex++]:'')).join('');
 while(imageIndex<images.length)body+=images[imageIndex++];
 body+='<h2>An Illustrative Scenario</h2>'+d.example.map(p).join('')+tail+sources;
 html=html.replace(match[0],match[1]+body+match[3]);
 html=html.replace(/("dateModified"\s*:\s*")[^"]+/, '$12026-10-14');
 if((html.match(/<img\b/g)||[]).length!==(fs.readFileSync(file,'utf8').match(/<img\b/g)||[]).length)throw Error('Image loss');
 fs.writeFileSync(file,html);
 console.log('Rewrote safety-sensitive content: '+slug);
}
