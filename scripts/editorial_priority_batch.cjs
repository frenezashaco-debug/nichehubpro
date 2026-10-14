// Targeted, reviewed corrections. Fail before writing if an expected passage is absent.
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const plain=s=>s.replace(/<[^>]*>/g,'').replace(/\s+/g,' ').trim();
const changes={
'how-to-build-a-stress-resistant-morning-routine':[
['Most people start their day in reactive mode.', 'A rushed morning can leave little room to choose what happens next. Messages, caregiving, and travel may compete for the same few minutes. Identify one avoidable pressure rather than treating a busy start as evidence of nervous-system damage.'],
['When your morning feels chaotic,', 'Morning pressure can have practical causes: a missing item, an unclear departure time, or more tasks than the available time permits. Write down the first bottleneck and see whether preparing it the night before would help.'],
['Checking your phone within seconds', 'If notifications delay an essential task, try checking them after that task instead. Keep urgent contacts reachable.'],
['Having no plan means', 'An unclear priority can add decisions to an already crowded morning. Write down the next necessary action.'],
['A stress resilient daily routine starts', 'A useful morning plan leaves room for changing circumstances. Choose a minimum version for a difficult day instead of expecting a routine to protect you from every source of stress.'],
['Here is what the research specifically points', 'The ideas below are practical options, not a research-tested package. Try one that addresses the obstacle you identified.'],
['Journaling or planning ahead reduces', 'Writing down a task keeps the reminder somewhere you can consult. Use one brief note rather than a long daily exercise if time is tight.'],
['Below are specific habits that build', 'These optional habits serve different purposes. Select the one that solves a practical problem for you rather than adding the whole list.'],
['Gratitude journaling:', '<strong>Gratitude journaling:</strong> If reflection feels useful, write one specific thing you appreciated. Skip it when it becomes forced positivity or another obligation.'],
['Most people who try to build', 'A routine can be difficult to maintain when it assumes more time or control than you have. Compare the plan with a real workday before blaming your motivation.'],
['Mistake 4 - Checking your phone', '<strong>Mistake 4: Treating every notification as urgent.</strong> Separate required messages from optional browsing. Choose a check-in time that fits your responsibilities; no universal delay changes stress hormones.'],
['According to research published by the European Journal', 'Habit development varies between people and activities. A published average is not a deadline for your own routine. Review whether the action fits your life rather than waiting for a particular day to feel automatic.'],
['Stress will always show up.', 'A routine cannot remove difficult working conditions or personal circumstances. Use it to handle a manageable part of the morning, and seek practical or professional support for problems it cannot address.'],
['Maria was a 34-year-old', '<strong>Invented planning example:</strong> Maria needs to leave for work while also responding to urgent family messages. She notices that searching for her bag delays her more than the necessary phone call. She chooses to pack the bag in the evening.'],
['She made one change first.', 'On an evening when packing is not possible, Maria uses a short essentials list by the door. This example illustrates a fallback, not an observed improvement in anxiety or performance. Pick a bottleneck and design your own minimum version.'],
['Stress will keep showing up.', 'Tomorrow does not need to be a test of discipline. Try the smallest useful adjustment, and revise it if it adds pressure rather than reducing a practical obstacle.']
],
'how-to-stay-motivated':[
["You're not lazy.", 'Difficulty starting is not enough information to judge your character. Check whether the task is clear, affordable, meaningful, and realistic before choosing a strategy.'],
['The fix starts here:', 'Start with one action whose outcome you can observe. Opening the course and answering one question gives you more information than waiting to feel ready. Use the result to decide what support or preparation you need next.'],
["Your brain's dopamine system resets", 'Motivation can vary across tasks and circumstances. Record the obstacle rather than assuming a daily chemical reset.'],
['External rewards (tracking progress', 'A progress record is optional. Keep one only if it helps you choose the next step.'],
['Start by identifying one specific moment', 'Identify a moment when starting becomes difficult and write down what is missing. If the task is unclear, ask for clarification; if the workload is excessive, reconsider the commitment.'],
["Watch for these specific patterns", 'Look for patterns you can describe without diagnosing yourself. Notice the task, the surrounding demands, and what you did next.'],
['The honeymoon phase of any goal', 'A new goal may feel different once its practical demands become clear. Check the required time, cost, and support instead of interpreting a change in enthusiasm as proof of a dopamine problem.'],
['Novelty and effort can change', 'Review a stalled goal by separating interest from feasibility. You might still value the outcome while lacking time or instructions. Change the constraint you can identify rather than trying to reset a reward system.'],
['The solution is understanding', 'A visible next step can make a vague project easier to approach. Write down a small deliverable and the information it requires; novelty is optional, not a biological requirement.'],
['Visible progress (tracking, data', 'Track completed work if that helps you plan; a checkmark does not measure dopamine.'],
['Changing your method or location', 'Change location only when it addresses a specific obstacle, such as noise or missing equipment.'],
['This week, change one thing', 'This week, test one change against a practical criterion. For example, ask whether a quieter room lets you finish a draft. Keep the change only if its benefit is worth its cost.'],
['Delete or silence social media apps', 'Silence optional notifications during a chosen task while keeping necessary communication available.'],
['Environmental cues can make', 'A visible reminder can help you remember a planned task. Place the course notebook beside the device you will use, then check whether that reminder is useful.'],
['Morning anchor:', '<strong>Starting cue:</strong> Link the next action to a convenient event, such as finishing lunch. A cue is a reminder, not a way to prime brain chemistry.'],
["Motivation isn't maintained", 'A system should be useful even on a difficult day. If the smallest planned step still feels unmanageable, reconsider the task or ask for support instead of treating the difficulty as failure.'],
['These five daily habits cost', 'Each habit below has a time and effort cost. Choose one, and remove it if recording or planning starts to displace the work itself.'],
['Start with just morning why', 'Choose one reminder and one review point that fit your schedule. Review whether you started more easily; do not interpret anticipation or resistance as a measurement of brain chemistry.'],
['Sarah had been trying', '<strong>Invented planning example:</strong> Sarah wants to finish a course but cannot protect an hour after work. She lists the remaining assignments and asks a study partner to help her choose one small task for their next meeting.'],
['Three months later,', 'The pair agree to review one practice answer rather than promise a completion date. If the meeting is cancelled, Sarah can send a question instead. This example demonstrates a fallback, not a reported exam result or recovery timeline.'],
['How to stay motivated stops', 'How to stay motivated is a practical question, not a test of willpower. Start by naming what makes this particular task difficult, and choose a response that fits the obstacle.'],
['Start today with just 10 minutes.', 'Choose one manageable action today. If you cannot begin, use that information to adjust the demand or seek support rather than forcing yourself to prove that the goal matters.']
],
'how-to-reset-your-mindset':[
['Knowing how to reset your mindset when', 'How to reset your mindset can mean pausing to reconsider one situation, not rewiring your brain on demand. Try writing what you know, what you are assuming, and one action you can take. Seek support when distress persists or daily life becomes difficult.'],
['You are not permanently stuck.', 'You do not need to promise yourself a transformation. Take one manageable step or ask someone appropriate for support; either can be a useful place to begin.']
],
'best-morning-habits-for-more-energy':[
['According to the National Sleep Foundation, sleep inertia.', 'Grogginess after waking does not identify its cause. If it regularly interferes with daily life, note your sleep schedule and symptoms for a healthcare professional rather than assuming that a morning habit will fix it.'],
['Your cortisol (the natural alertness hormone)', 'Choose a wake time that allows enough sleep; a routine is not a way to control your hormone levels.'],
['Key research takeaway:', 'Protecting sleep is more useful than adding an elaborate routine that shortens it. Start by checking whether the morning plan leaves adequate time for rest.'],
['Light exercise in the morning increases', 'If comfortable and appropriate, choose a movement activity you enjoy. Morning is not the only useful time to be active.'],
['Mindfulness for as little as', 'A quiet pause is optional. Keep it brief and stop if focusing inward increases distress.'],
['These are not opinions from', 'The following ideas are planning suggestions, not a tested treatment package. Select one that fits a specific need rather than expecting a guaranteed energy increase.'],
['2. Get natural light within', '<strong>2. Make room for daylight when practical.</strong> Spend some time outdoors if safe and accessible. Use normal eye and sun protection; no precise morning window guarantees alertness.'],
['10 minutes of morning movement increases', 'Choose a comfortable amount of movement instead of aiming for a promised change in brain oxygen.'],
['5. Eat a breakfast with protein.', '<strong>5. Plan food that fits your needs.</strong> If you eat breakfast, choose foods you can access and tolerate. Do not interpret tiredness as proof of a blood sugar problem; follow individualized advice for diabetes or other medical conditions.'],
['Avoid screens for 30-60 minutes', 'Allow a quieter period before bed if possible and reduce bright artificial light; avoid treating one screen-time rule as a guaranteed sleep fix.'],
['The National Sleep Foundation recommends', 'Both sleep duration and timing deserve attention. NHLBI advises allowing enough time for sleep and maintaining a regular schedule where possible. Do not shorten your sleep to fit more morning activities.'],
['Research from University College London found', 'Habits develop at different rates. A study average is not a deadline or a promise that the second week will feel easier. Review the action against your actual schedule and adjust its size.'],
['The habit stack method is particularly effective', 'An existing activity can serve as a reminder for a new one. Put the item you need near that cue and check whether the arrangement helps; it will not make every behavior automatic.'],
['Sarah was crushing it at work', '<strong>Invented planning example:</strong> Sarah feels tired during work and wants to understand her mornings. She notes her sleep opportunity and the activities fatigue interrupts, then arranges an assessment rather than assuming breakfast is the cause.'],
['Then she tried something simple:', 'While waiting, she simplifies one practical task by preparing her bag in the evening. This scenario shows how to reduce morning demands without claiming to treat fatigue. There is no observed recovery or promised deadline.']
],
'how-to-stop-self-sabotaging':[
['Your brain is trying to protect', 'The behavior may have several explanations; describe its context instead of assuming a protective brain response.'],
['The moment things start going well', 'A setback can happen at any stage of a project. Notice when avoidance appears in your own experience instead of assuming that success automatically triggers it.'],
['Stopping self-sabotage requires active', 'The five approaches below are practical experiments, not ranked treatments. Choose one observable behavior to change and review what happens without claiming to rewire your nervous system.'],
['Method 5: Slow Down Right Before', '<strong>Method 5: Check the next step before a deadline.</strong> Identify what is unfinished, ask for clarification where needed, and agree a realistic delivery plan. Do not assume every delay reflects fear of success.'],
['Midday: Progress Check-In', '<strong>Midday: Progress check-in.</strong> Note one completed action and one obstacle. Use the record to plan, not as evidence of a neurological change.'],
['Before Difficult Tasks: Grounding Practice', '<strong>Before difficult tasks:</strong> If a brief pause helps, notice your surroundings and name the next action. Skip the exercise if it distracts you or increases distress.']
],
'how-to-improve-concentration-naturally':[
['The good news is that your brain', 'Changes to your work conditions may make a task easier to manage. They do not prove that concentration difficulties can be resolved without medical care. Choose one practical adjustment and seek assessment when problems persist.'],
['No-phone morning block:', 'Optional notification-free period: choose a time that fits your responsibilities, without assuming it changes an attention baseline.'],
['Step 3 - Use structured work blocks.', '<strong>Step 3: Try a bounded work session.</strong> Choose one task and a realistic stopping point, then review your output and fatigue. A timer is an organizational tool, not a proven treatment. Our <a href="../articles/pomodoro-technique-explained-for-beginners.html">guide to using a Pomodoro timer</a> describes one option.'],
['Maya, a 29-year-old', '<strong>Invented planning example:</strong> Maya keeps switching away from a design brief. She notices that the client has not defined the required dimensions, so she asks for clarification before trying another concentration technique.'],
['After two weeks of fixing', 'Maya then tests a short session with the clarified brief and notes whether she can produce the requested draft. This example illustrates task design, not an ADHD assessment or evidence that lifestyle changes replace medication.']
],
'how-to-control-your-thoughts':[
['Your brain defaults to worst-case', 'Stressful situations can make threatening interpretations more noticeable; check the evidence for the particular thought.'],
['The practical takeaway here is simple.', 'Difficult thoughts are not a reason to blame yourself. Ask whether the situation calls for a practical action, a pause, or professional support rather than treating every thought as a faulty alarm.']
],
'best-focus-techniques-for-students':[
['The best focus techniques for students include', 'The best focus techniques for students depend on the task and the obstacle. A timer may help organize work, while practice questions reveal what you can recall. Try one method and check the quality of your work rather than expecting a guaranteed result within a week.'],
['The Pomodoro Technique is one of the most researched', 'The Pomodoro technique is a way to divide work into timed sessions and breaks. A common starting pattern is 25 minutes of work and a five-minute break, but those numbers are a convention, not a biological attention cycle. Adjust the session to the task.'],
['It works because it creates urgency', 'A visible stopping point may make a study session easier to begin. If a countdown makes you anxious or interrupts a useful task, use a task-based stopping point instead.'],
['Try each one for at least three days', 'Try one method on comparable assignments and note accuracy, completion, and effort. A short trial helps you make a practical choice; it cannot establish how your brain works. Our <a href="../articles/pomodoro-technique-explained-for-beginners.html">step-by-step Pomodoro guide</a> explains the timer option.'],
['A friend suggested he try one change:', 'In this invented example, Marcus tries putting optional notifications away for one practice set. He checks his answers and records which errors need more study. This is a way to compare study conditions, not a reported improvement in grades or study speed.'],
['Identifying which of these is your biggest', 'Choose an obstacle you can observe, such as missing instructions or repeated messages. Address that one first and check your work before adding another technique.']
]
};
const outputs=[];
for(const [slug,patches] of Object.entries(changes)){
 const file=path.join(root,'articles',slug+'.html');let html=fs.readFileSync(file,'utf8');
 for(const [prefix,replacement] of patches){
  let count=0;
  html=html.replace(/<(p|li)\b([^>]*)>([\s\S]*?)<\/\1>/g,(all,tag,attrs,inner)=>{
   if(!plain(inner).startsWith(prefix))return all;
   count++;return `<${tag}${attrs}>${replacement}</${tag}>`;
  });
  if(count!==1)throw Error(`${slug}: expected one '${prefix}', got ${count}`);
 }
 html=html.replace(/("dateModified"\s*:\s*")[^"]+/, '$12026-10-14');
 outputs.push([file,html]);
}
for(const [file,html]of outputs)fs.writeFileSync(file,html);
console.log(`Applied reviewed passage corrections to ${outputs.length} articles.`);
