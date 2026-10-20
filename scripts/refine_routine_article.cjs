const fs = require('fs');
const path = require('path');
const root = path.resolve(__dirname, '..');
const slug = 'why-your-brain-craves-routine-even-when-you-resist-it';
const file = path.join(root, 'articles', slug + '.html');
let html = fs.readFileSync(file, 'utf8');
const oldTitle = '7 Reasons Why Your Brain Craves Routine Even When You Resist It';
const title = 'Why Your Brain Craves Routine Even When You Resist It: 5 Practical Checks';
const oldMeta = html.match(/<meta name="description" content="([^"]+)"/)[1];
const meta = 'Why your brain craves routine even when you resist it: explore habits, check what helps, and try five flexible routine checks without making your day rigid.';
const p = s => `<p>${s}</p>\n`;
const ul = a => '<ul>' + a.map(s => `<li>${s}</li>`).join('') + '</ul>\n';
const sections = [
['What Is a Routine, and How Is It Different From a Habit?',
p('A routine is a sequence you repeat; a habit can become a response to a familiar cue. They are not identical. <strong>Check 1: name one repeated action and what usually starts it.</strong>') +
p('The NIMH describes habits as triggered behaviours that can continue with less conscious oversight. This does not mean every routine is automatic. Notice whether you deliberately choose your action or begin before thinking.') +
ul(['Cue: finishing breakfast.', 'Action: placing your keys beside your bag.', 'Practical purpose: knowing where to find them before leaving.', 'Review question: does this arrangement still suit your household?']) +
p('This distinction keeps the goal practical. You do not need to prove that your brain craves anything to organise your keys. Choose a repeated action that removes an actual inconvenience.') +
p('Repetition can make an action familiar without making it useful. Our guide to <a href="/articles/what-neuroplasticity-means-for-changing-your-habits.html">changing established habits</a> explores that distinction. Judge your routine by its consequences, not just its familiarity.') +
p('Wanting variety and using routines can coexist. A familiar starting point leaves room for different activities afterward. Keep a simple cue while allowing yourself to choose what follows.')],
['What Are the Signs That Your Routine Needs Adjusting?',
p('Missed practical needs are more useful clues than guesses about brain chemistry. <strong>Check 2: identify one recurring difficulty.</strong> Look for a missed break, misplaced item, or task without a clear starting point.') +
ul(['You repeatedly forget something needed before leaving home.', 'Your intended break disappears when work becomes busy.', 'A routine takes longer than the benefit seems worth.', 'A small schedule change makes your plan impossible to follow.']) +
p('These observations do not diagnose a shortage of routine. Concentration problems and irritability can have different explanations. Read about <a href="/articles/signs-of-mental-exhaustion.html">recognising mental exhaustion</a> without assuming a single cause.') +
p('Stress or persistent anxiety deserves attention in its own right. NIMH distinguishes anxiety disorders from occasional worry and notes their interference with daily life. Seek professional support when symptoms persist, interfere, or concern you.') +
p('Your circumstances may be the main obstacle. Caregiving, shift work, transport, or workload can make a fixed timetable unrealistic. Identify what support or flexibility you need before adding another rule.')],
['Why Can Familiar Routines Feel Easier?',
p('A familiar cue can reduce the need to decide how to start. NIMH notes that habits can free cognitive resources, but this is not proof of a single mental fuel tank. <strong>Check 3: find what the routine actually simplifies.</strong>') +
ul(['Preparation: the item you need is already in place.', 'Sequence: you know the next step without making a new plan.', 'Reminder: an existing event prompts the intended action.', 'Coordination: another person knows when you are available.']) +
p('These are practical explanations, not measurements of your nervous system. A tidy starting point may help even when you still feel stressed. Evaluate whether starting becomes easier rather than expecting a particular mood.') +
p('A repeated action can also outlast its purpose. Familiarity alone does not show that it serves your current needs. Keep the helpful cue, but change the action if its costs outweigh its benefits.') +
p('Task demands matter alongside habits. Our guide to <a href="/articles/what-cognitive-load-does-to-your-decision-making.html">understanding cognitive load when choosing</a> separates task difficulty from fuel-tank claims. Put necessary information in view before deciding.') +
p('Predictability is not a universal treatment for anxiety. The cited resources do not establish that a schedule switches off threat detection. Treat organisation as practical support, not a substitute for appropriate care.')],
['How Can You Build a Routine Without Feeling Trapped?',
p('A flexible plan includes a smaller version for difficult days. <strong>Check 4: choose an action, a cue, and a fallback.</strong> Start with a low-stakes activity that fits your actual responsibilities.') +
ul(['Action: prepare the bag you need tomorrow.', 'Cue: after putting away dinner.', 'Fallback: place just the essential item beside the door.', 'Exception: change the cue when your shift or family plans change.']) +
p('A cue tied to an event can fit variable schedules better than an exact hour. This is a planning option, not a proven solution for everyone. Compare it with a time-based reminder and choose the easier fit.') +
p('Protecting rest matters more than completing a checklist. Do not shorten sleep to maintain a routine, especially around changing shifts. Adjust the plan to your available rest and seek personalised guidance when needed.') +
p('Small actions are easier to revise than elaborate systems. See <a href="/articles/why-small-habits-create-big-results.html">starting with a manageable habit</a> for related planning ideas. Choose one action before adding more.') +
p('A missed attempt is information about the plan. The cue may be inconvenient or the action too large. Change one of those features before deciding that you lack discipline.')],
['How Can You Review Your Routine Daily?',
p('A brief review can reveal whether your plan is useful. <strong>Check 5: record what happened and one adjustment.</strong> The worksheet below is an editorial planning exercise, not a clinical assessment.') +
ul(['Cue: what event was meant to start the action?', 'Action: what did you actually do?', 'Friction: what made it harder or easier?', 'Fallback: was the smaller version available?', 'Next attempt: what will you keep or change?']) +
p('For example, write: after dinner, packed my bag, could not find my charger, placed a spare cable beside the bag. This records a specific obstacle. Use equally concrete notes for your own action.') +
p('Try a seven-day review window if that is manageable. Seven days is an organisational choice, not a deadline for habit formation or improved health. Review convenience and feasibility rather than expecting a transformation.') +
p('General stress-management guidance can inform the activity you choose. The CDC discusses sleep, movement, relaxation, and connection. Select something appropriate to your circumstances rather than copying every suggestion.') +
p('Daily habits should support living, not become another source of pressure. Our guide to <a href="/articles/daily-habits-for-better-mental-health.html">building sustainable daily habits</a> offers related ideas. Drop a tracking method if it adds work without helping.') +
p('Persistent distress needs more than a worksheet. If routines become restrictive or symptoms interfere with ordinary activities, discuss that with a qualified professional. Bring your observations rather than trying to diagnose yourself.')]
];
for (let i = 0; i < sections.length; i++) {
  const id = `sec-${i + 1}`;
  const re = new RegExp(`<h2 id="${id}">[\\s\\S]*?</h2>\\s*<p>[\\s\\S]*?(?=\\s*<(?:img|h2|div class="inline-promo"))`);
  if (!re.test(html)) throw Error('Missing section ' + id);
  html = html.replace(re, `<h2 id="${id}">${sections[i][0]}</h2>\n${sections[i][1]}`);
  html = html.replace(new RegExp(`(<a href="#${id}">)[^<]*(</a>)`), `$1${sections[i][0]}$2`);
}
html = html.replace(/(<img[^>]+loading="eager"[^>]*>)\s*<p>[\s\S]*?(?=\s*<div class="tldr")/,
 '$1\n' + p('Why your brain craves routine even when you resist it can feel personal: you want freedom but reach for familiar patterns. Start by noticing one routine you choose and one you dislike.') +
 p('A preference for familiarity is not a diagnosis or a character flaw. Habits and deliberate routines overlap without being the same. Separate what feels familiar from what actually helps.') +
 p('This guide offers five checks for making everyday structure more flexible. Each check focuses on a practical decision, not a promise about your brain. Try one before changing your whole schedule.'));
html = html.replace(/(<div class="tldr">)\s*<p>[\s\S]*?<\/p>/, '$1' +
 p('Why your brain craves routine even when you resist it is partly a question about familiar cues and repeated actions, not a universal need for rigid schedules. Use the five checks below to keep helpful structure and change what no longer fits.'));
html = html.replace(/(<h2 id="real-life">[^<]*<\/h2>)\s*<p>[\s\S]*?(?=\s*<div class="author-block")/, '$1' +
 p('Illustrative scenario: someone with changing work shifts keeps forgetting their charger. They choose packing a bag after their main meal as a cue, rather than setting a fixed evening alarm. Use this invented example to identify a cue that fits your day.') +
 p('On a busy day, their fallback is simply putting the charger beside the door. The example illustrates a planning decision, not an observed health improvement. Make your own fallback small enough to use when the full routine is impractical.'));
const answers = [
 'You can want variety while finding familiar actions convenient. Habitual responses may begin from familiar cues. Identify which parts help and leave room to change the rest.',
 'That depends on the habit and its effects. Familiarity alone does not make an action beneficial. Keep routines that serve your needs and reconsider those that restrict daily life.',
 'A change may require new planning or interrupt something you expected. Discomfort does not identify a single brain mechanism. Make an alternative plan, and seek support if distress is persistent or disruptive.',
 'There is no deadline established by this guide. A routine can be planned before it becomes habitual. Use a short review period to check feasibility, not to demand automatic behaviour.',
 'A rigid routine can become burdensome when it prevents needed flexibility. If distress about changing it interferes with daily activities, speak with a qualified professional. This article cannot determine the cause.'
];
let n = 0;
html = html.replace(/<div class="faq-a">[\s\S]*?<\/div>/g, () => `<div class="faq-a">${answers[n++]}</div>`);
if (n !== 5) throw Error('Unexpected FAQ count');
html = html.replace(/(<h2>Where to Go From Here<\/h2>)\s*<p>[\s\S]*?(?=\s*<div)/, '$1' +
 p('A useful routine makes something easier without taking over your day. You can keep familiar cues and still allow choice. Pick one small action that addresses a real inconvenience.') +
 p('Your first plan does not need to be permanent. An awkward cue or oversized action can be changed. Give yourself a fallback and review what happens.') +
 p('Support is available when the difficulty goes beyond organisation. Persistent distress deserves attention even when a routine looks sensible. Ask for help rather than treating the checklist as a test of character.'));
html = html.replaceAll(oldTitle, title).replaceAll(oldMeta, meta);
html = html.replace('7 Reasons Why Your Brain Craves Routine Even When You R...', 'Why Your Brain Craves Routine: 5 Practical Checks');
html = html.replace('"dateModified": "2026-10-19"', '"dateModified": "2026-10-20"');
html = html.replace('Source links are listed for further reading and require editorial verification before publication. They do not make this article a substitute for professional advice.',
 'Sources checked on October 20, 2026 for the limited points described below. The five-check worksheet is an editorial planning exercise, not a clinically validated intervention.');
html = html.replace('Centers for Disease Control and Prevention - Living with a Mental Illness', 'CDC - Managing Stress');
html = html.replace('NIMH has funded research into how habits form and how the brain distinguishes between automatic and deliberate behaviour, suggesting repeated behaviours may shift into more automatic processing over time.', 'NIMH defines habits as triggered behaviours that may continue without constant conscious oversight. This definition does not establish that every routine reduces anxiety.');
html = html.replace('Anxiety disorders involve persistent uncertainty and threat responses that the brain continues to register even in low-stakes situations, which is relevant to why unpredictability can feel disproportionately stressful.', 'NIMH distinguishes anxiety disorders from occasional worry and describes interference with daily activities. This resource does not diagnose distress about routine changes.');
html = html.replace('alt="Man closing laptop in home office as daily routine anchor"', 'alt="Man using a laptop at a home desk"');
// Keep published listings consistent without regenerating unrelated articles.
for (const rel of ['index.html', 'all-articles/index.html', 'mental-wellness/index.html', 'articles.js', 'api/articles.json']) {
  const f = path.join(root, rel);
  const before = fs.readFileSync(f, 'utf8');
  const after = before.replaceAll(oldTitle, title).replaceAll(oldMeta, meta)
    .replaceAll('Why your brain craves routine even when you resist it is one of those questions that can stop you mid-scroll and make you think. You tell yourself you...',
      'Use five practical checks to choose helpful cues, build a flexible fallback, and review your routine without treating it as a mental health test.');
  if (after !== before) fs.writeFileSync(f, after);
}
if (/—|&mdash;|require editorial verification|7 Reasons/.test(html)) throw Error('Editorial residue');
const body = html.slice(html.indexOf('<h2 id="sec-1">'), html.indexOf('<h2 id="real-life">'));
if ((body.match(/href="\/articles\//g) || []).length !== 5) throw Error('Expected five body links');
if ((body.match(/<h2 /g) || []).length !== 5) throw Error('Expected five sections');
if ((html.match(/<img /g) || []).length !== 4) throw Error('Images changed');
if (meta.length < 155 || meta.length > 160) throw Error('Meta length');
for (const block of html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)) JSON.parse(block[1]);
fs.writeFileSync(file, html);
console.log(`Revised ${slug}; five sections, five body links, five FAQs, four images preserved.`);
