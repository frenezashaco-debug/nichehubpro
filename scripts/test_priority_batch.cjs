const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const forbidden={
'how-to-build-a-stress-resistant-morning-routine':['fundamentally changed how her nervous system','lower cortisol levels, reduce amygdala'],
'how-to-stay-motivated':['dopamine system resets every 24 hours','Most people rebuild momentum within 48-72','Remove the unsupported','remove the unsupported'],
'how-to-reset-your-mindset':['Therapy accelerates the process','neural pathways built over years'],
'best-morning-habits-for-more-energy':['By day 14','reduces cortisol spikes later','Morning exercise is generally better'],
'how-to-stop-self-sabotaging':['requires active rewiring','These all serve the same purpose'],
'how-to-improve-concentration-naturally':['She did not take any medication','she reported feeling sharp'],
'morning-routine-for-a-healthy-lifestyle':['No sunglasses','Let the light hit your eyes directly','stabilizes your blood sugar for six hours'],
'how-to-control-your-thoughts':['Your brain defaults to worst-case'],
'how-to-stop-panic-attacks':['Your heart is safe','Dunk your face','Your five senses are always in safety','Once your heart is medically clear'],
'best-focus-techniques-for-students':['14 points higher','one of the most researched','Most research suggests 25 to 50']
};
for(const[slug,phrases]of Object.entries(forbidden)){
 const h=fs.readFileSync(path.join(root,'articles',slug+'.html'),'utf8');
 for(const phrase of phrases)assert(!h.includes(phrase),slug+': stale claim '+phrase);
 assert.equal((h.match(/<img\b/g)||[]).length,4,slug+': images');
 assert.equal((h.match(/class="faq-a"/g)||[]).length,5,slug+': FAQ');
 assert(h.includes('This article is for informational purposes only and does not replace professional medical advice.'),slug+': disclaimer');
 assert(h.includes('2026-10-14'),slug+': modification date');
 for(const m of h.matchAll(/<script[^>]*type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/g))JSON.parse(m[1]);
}
console.log('PASS: ten articles, four images each, five FAQs each, valid JSON-LD and removed-claim regression checks. Not a full medical review.');
