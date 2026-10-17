// Targeted editorial corrections. Does not certify the rest of an article.
const fs = require('node:fs');
const path = require('node:path');
const root = path.join(__dirname, '..');
const sleep = '<a href="https://www.nhlbi.nih.gov/health/sleep-deprivation">NHLBI guidance on sleep deficiency</a>';
const anxiety = '<a href="https://www.nimh.nih.gov/health/publications/generalized-anxiety-disorder-gad">NIMH guidance on generalized anxiety disorder</a>';
const fixes = [
 ['how-sleep-affects-mental-health', 'How sleep affects mental health is profound', `How sleep affects mental health varies between people. ${sleep} describes links with mood, concentration and depression, not a universal percentage increase in symptoms. Record your sleep difficulties and discuss persistent problems with a health professional.`],
 ['how-sleep-affects-mental-health', '<strong>The use point:</strong>', 'Sleep quality cannot be reduced to a fixed percentage explained by two habits. Keep a note of your sleep schedule and daytime symptoms, and seek help if difficulties persist rather than assuming a routine change will fix them.'],
 ['how-to-reduce-anxiety-naturally', 'Sleep deprivation amplifies anxiety 300%', `Sleep deficiency can affect mood and daily functioning, as described in ${sleep}. A fixed anxiety multiplier is not justified here. Protect time for sleep and seek advice when sleep problems or anxiety interfere with your day.`],
 ['fear-of-failure-anxiety', 'Fear of failure anxiety is one of', 'Fear of failure anxiety can make a task feel threatening before you start. Rather than guessing how common your experience is, identify the specific outcome you fear and one manageable step you can take with support.'],
 ['fear-of-failure-anxiety', 'The good news? Fear of failure anxiety is manageable.', 'Fear of failure anxiety deserves support when it limits your choices. The suggestions below are self-help options, not tested treatments or substitutes for therapy. Choose a small step, and consider professional help if avoidance persists.'],
 ['how-to-break-negative-thinking', 'How to break negative thinking starts', 'How to break negative thinking starts with noticing a recurring thought, not assigning a percentage to your thinking. Write down one thought, the situation that prompted it, and a more balanced interpretation you can test.'],
 ['how-to-build-confidence', "Real confidence isn't the absence", 'Confidence and self-doubt can coexist. Feeling uncertain does not establish how capable you are, so choose a small task with a clear finish point and use the result to decide what to practise next.'],
 ['how-to-deal-with-toxic-people', 'The reason you struggle to set boundaries', 'Setting boundaries can be difficult for many reasons, including fear of conflict or dependence on the other person. A relationship label cannot establish your history or diagnose either person. Identify the specific behaviour that concerns you and seek support to plan a safe response.'],
 ['how-to-improve-energy-naturally', 'Research shows that about 70%', 'Persistent tiredness does not have one explanation that an article can diagnose. Do not assume that food, water or stress explains it. Record when it occurs, any other symptoms, and medicines you take, and arrange a medical assessment if it continues.'],
 ['how-to-improve-energy-naturally', 'The shift from artificial energy', 'Energy changes do not follow a universal recovery schedule. Keep a short record of fatigue and its impact on normal activities, and use that record to explain the problem to a clinician rather than waiting for a promised improvement date.'],
 ['how-to-stop-worrying-about-the-future', 'Future worry is when', 'Future worry involves anticipating what could go wrong. A reassuring percentage cannot tell you whether a particular concern will happen. Separate one practical problem you can act on from a hypothetical worry you cannot resolve right now.'],
 ['how-to-stop-worrying', 'Research from cognitive behavioral therapy', `Cognitive behavioral therapy is a treatment option for generalized anxiety disorder, according to ${anxiety}. That does not establish a success rate or recovery deadline for the exercises on this page. If worry is disrupting daily life, ask a qualified professional about suitable treatment.`],
 ['productivity-system', 'The truth? Your productivity system', 'Your productivity system needs to fit your responsibilities and available time. There is no verified failure rate supplied here for productivity methods. Try one small change and review whether it actually helps you complete the work that matters.'],
 ['best-foods-for-better-sleep', 'Kiwis are scientifically proven', 'Kiwi can be a food choice if you enjoy it and tolerate it, but this guide cannot promise additional minutes of sleep or a percentage improvement. Avoid treating a food as a remedy for persistent insomnia; discuss ongoing sleep problems with a clinician.'],
 ['best-foods-for-better-sleep', 'Salmon is one of the most powerful sleep foods', 'Salmon can be part of a varied diet, but a particular serving schedule does not guarantee faster sleep onset. Choose foods around your preferences, allergies and dietary needs rather than a promised effect on sleep.']
];
const changed = new Set();
for (const [slug, start, replacement] of fixes) {
 const file = path.join(root, 'articles', slug + '.html');
 let text = fs.readFileSync(file, 'utf8');
 let count = 0;
 const next = text.replace(/<p\b[^>]*>[\s\S]*?<\/p>/g, paragraph => {
   if (paragraph.replace(/^<p\b[^>]*>/, '').startsWith(start)) {
     count++; return '<p>' + replacement + '</p>';
   }
   return paragraph;
 });
 if (count > 1) throw new Error('Ambiguous correction: ' + slug + ' ' + start);
 if (!count && !text.includes(replacement)) throw new Error('Missing correction target: ' + slug + ' ' + start);
 if (next !== text) { fs.writeFileSync(file, next); changed.add(slug); }
}
console.log(`Applied ${fixes.length} targeted corrections across ${changed.size} articles.`);
