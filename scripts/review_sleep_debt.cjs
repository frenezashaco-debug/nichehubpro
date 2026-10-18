// Scoped editorial corrections, based on CDC and NHLBI pages consulted 2026-10-18.
const fs = require('node:fs');
const file = 'articles/how-sleep-debt-silently-drains-your-daily-performance.html';
let h = fs.readFileSync(file, 'utf8');
const changes = [
['It is not a medical diagnosis, but', 'Sleep needs vary with age. The <a href="https://www.cdc.gov/sleep/about/index.html">CDC sleep recommendations</a> specify at least seven hours for adults aged 18 to 60, seven to nine for ages 61 to 64, and seven to eight from age 65. Use the appropriate range when reviewing your schedule.'],
['The tricky part is that', 'Feeling accustomed to short nights does not establish that your performance is unaffected. NHLBI notes that people can underestimate sleep-related impairment; compare your sleep record with mistakes and daytime sleepiness rather than relying on familiarity.'],
['<strong>Sleeping longer on days off', 'Sleeping longer on days off can accompany insufficient weekday sleep, but it does not establish a diagnosis. Note the difference in your diary and discuss persistent unrefreshing sleep with a healthcare professional.'],
['If you recognise four or more', 'There is no validated symptom-count threshold in this checklist. Persistent sleepiness or impaired daily functioning deserves attention even with only one symptom; explore <a href="/articles/why-you-feel-tired-all-the-time.html">common reasons behind constant tiredness</a> and seek assessment when needed.'],
['Concentration is usually the first', 'Sleep deficiency can affect attention, memory and reaction time, but symptoms do not follow a fixed order. The <a href="https://www.nhlbi.nih.gov/health/sleep-deprivation/health-effects">NHLBI overview of sleep and performance</a> explains these effects; record the tasks where you notice difficulty.'],
['Physically, your body is also', 'Sleep supports immune function and metabolic regulation, although these processes also operate while you are awake. Treat adequate sleep as one part of health rather than trying to identify a hormone or blood-sugar problem from fatigue alone.'],
['The mood piece is significant', 'Sleep and mood problems can occur together, and a diary cannot establish which caused the other. Record both and discuss persistent low mood or anxiety with a clinician rather than assuming sleep alone explains it.'],
['Most people attempt to fix', 'A recovery plan needs enough opportunity to sleep, not just a fixed alarm. Identify what regularly shortens your night before deciding which part of your schedule can change.'],
['The most common mistake is the weekend', 'Large changes between weekday and weekend sleep timing can disrupt your sleep-wake rhythm. NHLBI suggests keeping the difference to about an hour; consider a more regular schedule where work and caring responsibilities allow.'],
['<strong>Gradual, consistent adjustment works', 'An earlier wind-down can be a manageable scheduling experiment, but it is not a proven repayment formula. Try a small change you can sustain and assess daytime function without expecting recovery by a fixed date.'],
['A practical experiment to try:', 'A consistent wake time is useful only alongside enough time for sleep. Work backward from necessary morning commitments to protect a realistic sleep window, and seek advice if you remain unable to sleep despite adequate opportunity.'],
['<strong>Light exposure in the morning', 'Daylight and activity can support a regular routine. The <a href="https://www.nhlbi.nih.gov/health/sleep-deprivation/healthy-sleep-habits">NHLBI healthy sleep habits guidance</a> recommends time outdoors when possible; fit this around your schedule rather than treating a specific number of minutes as a treatment.'],
['Hydration also plays a role', 'Fatigue has multiple possible explanations, so a sleep diary is a record rather than a diagnostic test. Keep notes on sleep and daytime function, then bring them to an appointment if difficulties persist.'],
['Source links are listed for further reading', 'References below support the sleep-duration, daily-function and routine guidance. The diary is a practical planning aid, not a diagnostic tool or a guaranteed recovery programme.'],
];
for (const [prefix, replacement] of changes) {
 let found = false;
 h = h.replace(/<p(?:\s[^>]*)?>[\s\S]*?<\/p>/g, p => {
   const body = p.replace(/^<p(?:\s[^>]*)?>/, '');
   if (!body.startsWith(prefix)) return p;
   found = true; return p.replace(body, replacement + '</p>');
 });
 if (!found) throw Error('Missing paragraph: ' + prefix);
}
h = h.replace('Set a consistent wake time first, before worrying about bedtime', 'Protect enough time for sleep alongside a reasonably consistent wake time')
 .replace('Get natural light in the morning, even five to ten minutes outside can help', 'Spend time outdoors when possible; adapt timing to your work and sleep schedule')
 .replace('Physical coordination and balance may be subtly affected', 'Reaction times may slow, making safety-sensitive tasks harder')
 .replace('Recovery from exercise takes longer when sleep is inadequate', 'Remembering instructions and finishing tasks can become harder');
const diary = `<h3>A seven-day sleep record you can actually use</h3>
<p>A simple record helps separate time in bed from estimated time asleep. Copy these fields into a notebook each morning; estimates are enough, so avoid repeatedly checking the clock overnight.</p>
<ul><li>Date and work or rest day</li><li>Time you went to bed and approximate time you fell asleep</li><li>Night awakenings and final wake time</li><li>Naps, caffeine, alcohol and medication timing</li><li>Daytime sleepiness and one concrete difficulty, such as losing your place while reading</li></ul>
<p>For example, 11 p.m. to 7 a.m. is eight hours in bed. If falling asleep took 30 minutes and awakenings totalled another 30, your estimate is seven hours asleep; use that distinction when reviewing the week.</p>
<p>At the end of the week, identify one recurring barrier and one feasible adjustment. Bring the record to a clinician if sleep remains unrefreshing, you gasp during sleep, or daytime sleepiness affects safety.</p>
<p><strong>Do not drive or operate machinery when sleepy.</strong> Arrange another way to travel or stop in a safe place; a diary or extra coffee does not establish that you are safe to continue.</p>
`;
h = h.replace('<h3 id="sec-6">', diary + '\n<h3 id="sec-6">');
h = h.replace(/<li style="font-size:0\.82rem[^>]*>[\s\S]*?<\/li>/g, '');
h = h.replace(/(<p[^>]*>References below support[\s\S]*?<\/p>\s*<ul[^>]*>)/, '$1\n<li><a href="https://www.cdc.gov/sleep/about/index.html">CDC: age-specific sleep duration, sleep quality and diary fields</a></li>\n<li><a href="https://www.nhlbi.nih.gov/health/sleep-deprivation/health-effects">NHLBI: attention, memory, daytime impairment and safety</a></li>\n<li><a href="https://www.nhlbi.nih.gov/health/sleep-deprivation/healthy-sleep-habits">NHLBI: sleep timing, caffeine, naps and shift work</a></li>');
// Remove unsupported numerical FAQ threshold and recovery timeline in both visible and structured answers.
h = h.replaceAll('Consistently getting adequate sleep across several weeks may help your body and mind return to a better baseline.', 'Recovery varies, and no fixed number of nights guarantees that all effects have resolved.')
 .replaceAll('regularly sleeping two or more hours less than you need', 'regularly sleeping less than you need');
h = h.replace(/"dateModified":\s*"[^"]+"/, '"dateModified": "2026-10-18"');
fs.writeFileSync(file, h);
console.log('Sleep-debt claims corrected; references and diary added.');
