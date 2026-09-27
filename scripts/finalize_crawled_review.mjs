import fs from 'node:fs';
import assert from 'node:assert/strict';
import { batch } from './crawled_batch_content.mjs';
const remaining = ['improve-daily-routine','how-to-deal-with-anxiety-daily','how-to-focus-better-at-work','how-to-control-your-thoughts','why-you-feel-tired-all-the-time','how-to-detox-your-mind'];
const fixes = {
 'why-you-feel-tired-all-the-time': [
  [/The good news is that most causes[^<]+/, 'Fatigue has many possible causes and does not always improve with a routine change. Use these seven possibilities to prepare questions, not to diagnose yourself.'],
  [/Why you feel tired all the time usually[^<]+/, 'Why you feel tired all the time cannot be determined from a checklist. Record the pattern and discuss persistent or unexplained fatigue with a healthcare professional.'],
 ],
 'how-to-control-your-thoughts': [
  [/Do not skip the breathing step\.[^<]+/, 'Breathing is optional. Skip it if uncomfortable and return attention to something in the room.'],
  [/A ten-minute walk after lunch[^<]+/, 'Choose a brief movement break if it is comfortable and appropriate for your health; no duration guarantees relief.'],
  [/Do not skip physical movement\.[^<]+/, 'Adapt activity to your health and abilities rather than using exercise as a test of thought control.'],
  [/This sets a calmer baseline for the rest of the day\./, 'Notice whether this is useful without expecting it to determine the rest of your day.'],
 ],
 'how-to-deal-with-anxiety-daily': [
  [/It's a learned pattern your nervous system created for protection/, 'It may have multiple contributing factors that need individual assessment'],
  [/<strong>Practice 1:[^]*?(?=<\/li>)/, '<strong>Practice 1: Comfortable breathing</strong> - If you want to try it, breathe gently without forcing depth or holding your breath. Stop if uncomfortable and choose another activity.'],
  [/<strong>Practice 2:[^]*?(?=<\/li>)/, '<strong>Practice 2: A comfortable pause</strong> - Change position or sit somewhere quiet if this feels useful. You do not need to tense painful muscles or complete a relaxation sequence.'],
  [/<strong>Practice 3:[^]*?(?=<\/li>)/, '<strong>Practice 3: Sort a worry</strong> - Write the concern and identify whether there is a practical action available. The <a href="https://www.nhs.uk/every-mind-matters/mental-wellbeing-tips/self-help-cbt-techniques/tackling-your-worries/">NHS guide to tackling worries</a> offers a structured approach. Stop if the exercise increases distress.'],
  [/<strong>Practice 4:[^]*?(?=<\/li>)/, '<strong>Practice 4: Optional movement</strong> - Choose an activity suited to your health and abilities. Movement is not proof that you are safe and is not a substitute for treatment.'],
  [/<p>Daily anxiety management isn't[^]*?<\/p>/, '<p>Daily anxiety management should leave room for both practical coping and professional care. Choose support based on your needs rather than expecting a perfect routine to resolve symptoms.</p>'],
  [/<p>Start today with box breathing[^]*?<\/p>/, '<p>Choose one comfortable action today, or arrange an appointment if anxiety is limiting your life. You do not need to wait for a self-help routine to work before asking for help.</p>'],
 ],
};
let sitemap = fs.readFileSync('sitemap.xml', 'utf8');
for (const slug of [...Object.keys(batch), ...remaining]) {
 const path = `articles/${slug}.html`;
 let html = fs.readFileSync(path, 'utf8');
 for (const [re, value] of fixes[slug] || []) {
  assert(re.test(html), `${slug}: missing repair match`);
  html = html.replace(re, value);
 }
 const desc = html.match(/<meta name="description" content="([^"]+)"/)[1];
 html = html.replace(/(<meta property="og:description" content=")[^"]*/, '$1' + desc);
 html = html.replace(/("description"\s*:\s*")[^"]*"/, '$1' + desc + '"');
 // Restore heading anchors retained by the original table of contents.
 let h = 0;
 if (!remaining.includes(slug)) html = html.replace(/<h2(?![^>]*\bid=)([^>]*)>/g, (_, attrs) => `<h2 id="sec-${++h}"${attrs}>`);
 if (remaining.includes(slug)) {
  const url = `https://nichehubpro.com/articles/${slug}.html`;
  sitemap = sitemap.replace(/<url>[^]*?<\/url>/g, entry => entry.includes(`<loc>${url}</loc>`) ? entry.replace(/<lastmod>[^<]+/, '<lastmod>2026-09-27') : entry);
 }
 for (const script of html.matchAll(/<script type="application\/ld\+json">([^]*?)<\/script>/g)) JSON.parse(script[1]);
 assert.equal((html.match(/class="faq-a"/g) || []).length, 5, slug + ' FAQ');
 assert(/Sources|References/.test(html), slug + ' sources');
 assert(!/<p>(?:(?!<\/p>)[^])*?<h2/.test(html.slice(html.indexOf('<article'))), slug + ' unclosed paragraph');
 fs.writeFileSync(path, html);
 console.log(`PASS ${slug}: FAQ, sources, JSON-LD, paragraph structure`);
}
fs.writeFileSync('sitemap.xml', sitemap);
