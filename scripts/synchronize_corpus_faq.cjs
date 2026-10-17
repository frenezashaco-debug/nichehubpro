const fs = require('node:fs');
const path = require('node:path');
const root = path.join(__dirname, '..');
const replacements = {
 'anxiety-before-sleep': [
  ['Why do I feel anxious when I go to bed?', 'Bedtime anxiety can have several contributing factors. Notice the pattern and its effect on sleep rather than assuming one cause. Discuss persistent symptoms with a qualified clinician.'],
  ['What can I try when worries interrupt bedtime?', 'Consider a comfortable wind-down activity or write down a practical concern to review later. Stop exercises that increase distress, and seek support when sleep problems continue.'],
  ['Should I continue a breathing exercise that makes me more anxious?', 'Stop if it increases distress or dizziness. Let breathing return to its normal comfortable pattern and consider another support option. Seek appropriate care for new or severe breathing symptoms.'],
  ['Is insomnia always caused by anxiety?', 'No. Difficulty sleeping can have several explanations. Record the pattern, daytime symptoms and medicines, and seek assessment rather than diagnosing the cause yourself.'],
  ['When should I seek help for anxiety before sleep?', 'Seek professional advice when anxiety or sleep problems persist, worsen or interfere with daily functioning. Describe what has changed and how it affects you.']
 ],
 'benefits-of-walking-daily': [
  ['How much walking should I start with?', 'Choose an amount and route that fit your ability and health. A manageable starting point is more useful than a universal target. Ask for advice when symptoms or health conditions limit activity.'],
  ['Can walking replace anxiety treatment?', 'Walking can be part of self-care when suitable, but it does not replace assessment or prescribed treatment for anxiety. Discuss an appropriate plan with your clinician.'],
  ['Do I have to reach ten thousand steps every day?', 'This guide does not require a universal step target. Plan activity around your ability, circumstances and any medical advice, then review what is manageable.'],
  ['What should I do if walking causes pain or breathing difficulty?', 'Stop if activity causes concerning symptoms and seek appropriate assessment. New or severe chest pain or breathing difficulty needs urgent medical help.'],
  ['How can I make a walking plan easier to maintain?', 'Choose an accessible route and a realistic opportunity, and consider weather, lighting and support needs. Change the plan when circumstances make it unsuitable.']
 ],
 'signs-of-mental-exhaustion': [
  ['Is mental exhaustion a diagnosis?', 'The phrase describes an experience and does not establish its cause. Describe fatigue, concentration problems or mood changes to a qualified professional if they persist.'],
  ['Could persistent exhaustion have a medical cause?', 'Persistent tiredness can have several explanations. Record other symptoms, sleep and medicines, and seek assessment rather than assuming stress is the only cause.'],
  ['Is rest always enough to recover?', 'Needs differ. Rest can be important, but ongoing symptoms may also need assessment and changes to workload or support. Seek advice when difficulties continue.'],
  ['What should I record before an appointment?', 'Note when symptoms began, sleep changes, medicines, other physical or mood symptoms, and their effect on daily activities. Bring the record to your appointment.'],
  ['When do physical symptoms need urgent attention?', 'Do not assume new or severe chest pain or breathing difficulty is exhaustion. Seek urgent medical help for concerning symptoms. Persistent non-urgent symptoms also deserve assessment.']
 ]
};
function plain(text) {
 return text.replace(/<[^>]+>/g, ' ').replace(/&#x([a-f0-9]+);/gi, (_, n) => String.fromCodePoint(parseInt(n, 16)))
  .replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(Number(n))).replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&apos;/g, "'").replace(/&nbsp;/g, ' ').replace(/\s+/g, ' ').trim();
}
let changed = 0;
for (const name of fs.readdirSync(path.join(root, 'articles')).filter(n => n.endsWith('.html'))) {
 const file = path.join(root, 'articles', name), slug = name.slice(0, -5);
 const original = fs.readFileSync(file, 'utf8');
 let h = original;
 if (replacements[slug]) {
  const container = h.match(/<div class="(?:faq|faq-section)"[^>]*>/);
  const start = container ? container.index : -1;
  if (start < 0) throw Error('Missing FAQ container: ' + slug);
  const tags = /<\/?div\b[^>]*>/g;
  tags.lastIndex = start;
  let depth = 0, end;
  for (let match; (match = tags.exec(h));) {
   depth += match[0].startsWith('</') ? -1 : 1;
   if (!depth) { end = tags.lastIndex; break; }
  }
  if (!end) throw Error('Unclosed FAQ container: ' + slug);
  const markup = container[0] + (container[0].includes('faq-section') ? '<h2>Frequently Asked Questions</h2>' : '') + replacements[slug].map(([q, a]) => '<div class="faq-item"><button class="faq-q">' + q + '<span class="faq-icon">+</span></button><div class="faq-a">' + a + '</div></div>').join('\n') + '</div>';
  h = h.slice(0, start) + markup + h.slice(end);
 }
 if (slug === 'why-you-feel-mentally-drained') h = h.replace(/(<div class="faq-item">)<h3>([^<]+)<\/h3>/g, '$1<button class="faq-q">$2<span class="faq-icon">+</span></button>');
 const faqs = [...h.matchAll(/<button\b[^>]*class="faq-q"[^>]*>([\s\S]*?)<span class="faq-icon">[\s\S]*?<div\b[^>]*class="faq-a"[^>]*>([\s\S]*?)<\/div>/g)]
  .map(m => ({'@type': 'Question', name: plain(m[1]), acceptedAnswer: {'@type': 'Answer', text: plain(m[2])}}));
 if (faqs.length !== 5) throw Error('Expected five questions in ' + slug);
 let hasSchema = false;
 h = h.replace(/(<script\b[^>]*type="application\/ld\+json"[^>]*>)([\s\S]*?)(<\/script>)/g, (full, open, raw, close) => {
  const data = JSON.parse(raw);
  let updated = false;
  const visit = value => {
   if (!value || typeof value !== 'object') return;
   if (value['@type'] === 'FAQPage') { hasSchema = true; if (JSON.stringify(value.mainEntity) !== JSON.stringify(faqs)) { value.mainEntity = faqs; updated = true; } }
   if (Array.isArray(value)) value.forEach(visit);
   if (value['@graph']) value['@graph'].forEach(visit);
  };
  visit(data);
  return updated ? open + JSON.stringify(data, null, 2) + close : full;
 });
 if (!hasSchema) h = h.replace('</head>', '<script type="application/ld+json">' + JSON.stringify({'@context': 'https://schema.org', '@type': 'FAQPage', mainEntity: faqs}) + '</script>\n</head>');
 if (h !== original) { fs.writeFileSync(file, h); changed++; }
}
console.log(`Five visible FAQs confirmed in all articles; synchronized/added structured answers in ${changed} files.`);
