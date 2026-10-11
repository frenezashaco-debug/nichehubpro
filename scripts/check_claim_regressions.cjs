// Narrow regression checks, not a fact-check or content-quality certification.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const checks = {
  'the-science-of-habit-formation-explained-simply': ['Without all three parts of the loop working together', 'old habit pathway stays in the brain', 'The brain does the rest over time'],
  'what-neuroplasticity-means-for-changing-your-habits': ['old habit pathway weakens from lack of use', 'You build a competing pathway that becomes stronger'],
  'how-to-recover-focus-after-a-distraction': ['This signals to your nervous system', 'almost always results in better output'],
  'how-to-stop-feeling-guilty-for-resting': ['Laziness is a choice', 'your nervous system stays activated longer than it should'],
  'how-to-build-energy-that-lasts-all-day-without-crashing': ['That drop is what many people feel as the classic afternoon slump', 'Eat something with protein within the first hour or two']
};
for (const [slug, phrases] of Object.entries(checks)) {
  const html = fs.readFileSync(path.join(__dirname, '..', 'articles', slug + '.html'), 'utf8');
  for (const phrase of phrases) assert(!html.includes(phrase), `${slug}: removed claim returned: ${phrase}`);
  assert.equal((html.match(/class="faq-a"/g) || []).length, 5, `${slug}: expected five FAQ answers`);
  assert(html.includes('Sources &amp; References'), `${slug}: missing sources section`);
}
console.log('PASS: removed-claim regressions, five FAQ answers and source sections across five guides.');
