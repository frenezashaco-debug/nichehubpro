// Targeted editorial corrections. Deliberately preserves navigation, images and sources.
import fs from 'node:fs';
const patches = {
 'improve-daily-routine': [
  ['The good news?', 'Small routine changes are experiments, not promises of a transformed life. Choose one manageable change and review whether it fits your responsibilities.'],
  ['To improve daily routine for success,', 'To improve daily routine, choose one specific action, a reliable reminder, and a fallback for difficult days. Review what helped before adding more habits.'],
  ['The biggest reason routines fail', 'A routine can become difficult when it contains too many changes, unrealistic timing, or tasks you cannot control. Identify the obstacle in your own schedule before choosing a smaller action.'],
  ['Sarah was a marketing manager', '<strong>Illustrative example, not a client story:</strong> A worker wants to stop starting every day in their inbox. Their proposed routine is to write the next step for one project before opening messages.'],
  ['In week one, Sarah', 'On meeting-heavy mornings, the fallback is one sentence rather than a full planning session. At the end of the week, they review which mornings allowed this and adjust the cue; no improvement in health or performance is assumed.'],
 ],
 'how-to-deal-with-anxiety-daily': [
  ['Daily anxiety also creates', 'Anxiety can involve both thoughts and physical sensations. A coping exercise is optional support, not a complete explanation or treatment; choose one that feels tolerable.'],
  ['The good news?', 'You do not have to prove that you are safe by completing a routine. If your situation is unsafe, prioritize practical help; if symptoms persist, seek an individual assessment.'],
  ['<strong>Check yourself', 'Notice whether worry affects activities you want or need to do. A symptom count in a blog cannot diagnose anxiety, so seek support based on distress and interference rather than a checklist score.'],
  ['Daily anxiety usually starts', 'Anxiety does not have one universal starting point. Rather than assuming a single cause, record when symptoms occur and discuss persistent difficulties with a qualified clinician.'],
  ['Your amygdala', 'A brain-based explanation cannot tell you why you personally feel anxious. Bring information about sleep, medicines, stress and physical symptoms to an appointment rather than diagnosing yourself from an article.'],
  ['Instead, daily anxiety management means', 'Daily coping should help you navigate your responsibilities without becoming another test to pass. Keep useful practices and ask for help when self-management is not enough.'],
  ['Fixing daily anxiety', 'The following practices are options to consider, not a five-part cure. Start with one comfortable choice and leave room for professional treatment.'],
  ['Habit stacking is the most effective', 'A familiar activity can serve as a reminder. After lunch, for example, briefly name a worry and decide whether it needs a practical next step; skip any exercise that increases distress.'],
  ['The science is clear:', 'There is no universal schedule that makes a coping practice effective. Choose a manageable frequency and assess whether it supports your daily functioning.'],
  ['Track your practices for two weeks', 'Brief notes can help you discuss your experience, but tracking does not guarantee lower anxiety. Stop tracking if it becomes repetitive checking or another source of pressure.'],
  ['Sarah spent three years', '<strong>Illustrative example, not a treatment outcome:</strong> A worker notices that worry is making them decline social plans. They write down the activities they are missing and arrange a conversation with a healthcare professional.'],
  ['When Sarah started', 'While waiting, they choose one manageable task and ask a friend for practical support. This example shows a way to prepare for help, not evidence that a breathing routine will resolve anxiety.'],
 ],
 'how-to-control-your-thoughts': [
  ['Your brain was not built', 'Difficult thoughts do not reveal a personal defect or one simple brain mechanism. Notice the situation in which they appear instead of assuming that every thought signals danger.'],
  ['<strong>Understanding this is the first step:', 'You do not need a neurological explanation to ask for help. If thoughts are distressing or interfere with daily life, describe their impact to a qualified professional.'],
  ['That small shift in language', 'Changing the wording is an experiment, not a guarantee of emotional distance. If it does not help, return to a safe activity rather than repeating it until it feels perfect.'],
  ['Here are the daily habits that consistently', 'Here are optional daily supports to adapt to your needs; none guarantees control over thoughts.'],
  ['None of these habits are dramatic.', 'A routine can support daily life without removing unwanted thoughts. Judge it by usefulness rather than how quiet your mind becomes.'],
  ['Most people approach thought control', 'Some approaches add pressure to an already difficult experience. Consider the pitfalls below without treating them as proof that you caused your symptoms.'],
 ],
 'why-you-feel-tired-all-the-time': [
  ['Sarah, 34,', '<strong>Illustrative example, not a medical case:</strong> A person feels persistently tired despite allowing enough time for sleep. They note their sleep schedule, medicines and the activities fatigue prevents before arranging an appointment.'],
  ['In four weeks, Sarah', 'They bring those notes to the clinician rather than assuming caffeine or dehydration explains everything. The next step depends on the assessment, not a promised improvement after a set number of days.'],
  ['Feeling tired all the time is not just', 'Persistent fatigue deserves attention, even when its cause is unclear. You do not have to demonstrate that you have tried every lifestyle change before asking for help.'],
  ['Start with one thing today.', 'Start by recording when tiredness occurs and how it affects your day. A clinician can decide whether tests are appropriate; do not choose supplements or a fixed blood-test panel from this article.'],
 ],
 'how-to-detox-your-mind': [
  ['Your mind is drowning', 'How to detox your mind is a popular phrase for wanting relief from mental overload. Your thoughts are not toxins, and having difficult thoughts does not make your mind unhealthy or dirty.'],
  ['The good news?', 'A mental reset is an informal self-care idea, not a medical cleansing process. Use the phrase cautiously and choose practical ways to organize concerns instead.'],
  ['This guide shows you exactly', 'This guide offers optional ways to sort worries and reduce avoidable distractions. Persistent distress needs appropriate support, not a stronger detox routine.'],
  ["You don't need to wait", 'Difficulty sleeping, concentrating or making decisions can have many causes. These experiences do not demonstrate mental toxicity; record the impact and seek help if they persist.'],
  ['<strong>Pay attention to these warning signs', '<strong>Use the following experiences as prompts for reflection, not a diagnostic checklist.</strong> Note which ones interfere with your daily activities.'],
  ['If three or more', 'There is no validated score for needing a mental detox. Seek support when distress affects your life, regardless of how many items seem familiar.'],
  ['Sarah spent her days', '<strong>Illustrative example, not a testimonial:</strong> A person keeps replaying a difficult meeting. They write two columns: what was actually said, and what they fear it meant.'],
  ['Sarah started with just', 'They identify one useful question to ask their colleague and put the page aside. This illustrates organizing a concern, not a promise that writing will improve sleep or treat anxiety.'],
  ["Your mind doesn't have to stay toxic.", 'Your mind does not need cleansing. You can make room for one useful next step without first getting rid of every uncomfortable thought.'],
  ['Start with the brain dump method', 'If writing helps, note one concern and one realistic action. Stop if writing increases repetitive worry, and try a different support or seek professional guidance.'],
  ['One week from now,', 'Choose a small, optional practice today. Keep it only if it is useful, and do not delay care while waiting for a self-help exercise to work.'],
 ],
 'how-to-focus-better-at-work': [
  ['Focus is a skill that builds', 'A useful system makes returning to work easier, not effortless. Choose one change you can control and discuss workload or availability expectations when the obstacle is outside your control.'],
 ],
};
const faqs = {
 'how-to-control-your-thoughts': [
 'You cannot guarantee which thoughts appear. You may be able to choose a helpful response, but results vary and persistent distress deserves professional support.',
 'Trying repeatedly to remove a thought may become frustrating. Notice it without treating it as an instruction, then return to a safe task; seek guidance if this is difficult.',
 'There is no dependable deadline. Evaluate whether a practice helps you function, rather than expecting thoughts to disappear within weeks.',
 'An unwanted thought is not the same as an intention. Seek professional help if thoughts cause distress or repeated checking; get urgent help if you intend to act on harmful thoughts or cannot stay safe.',
 'Try naming an object in the room and choosing one small next action. Comfortable breathing is optional, and no technique guarantees relief within a minute.',
 ],
 'why-you-feel-tired-all-the-time': [
 'Time in bed does not identify the cause of fatigue. Sleep disruption, health conditions and medicines are among possible factors; discuss persistent tiredness with a clinician.',
 'Some deficiencies can contribute, but fatigue alone cannot identify one. A clinician can decide whether testing or treatment is appropriate; avoid guessing with supplements.',
 'Anxiety can occur alongside fatigue, but it should not automatically be treated as the cause. Discuss both symptoms if they persist or limit daily activities.',
 'Persistent or unexplained fatigue deserves medical attention, particularly when it affects ordinary activities. Seek help sooner for severe or rapidly worsening symptoms.',
 'An afternoon dip does not identify a particular cause. Note sleep, meals, medicines and symptoms, and discuss recurring or severe fatigue rather than assuming a blood sugar problem.',
 ],
 'how-to-detox-your-mind': [
 'There is no established detox timeline because this is not a medical treatment. Keep a practice only if it helps you organize concerns or manage daily tasks.',
 'Yes. You can sort a concern on paper, reduce an avoidable notification or ask for support without meditating. None of these cleanses the mind.',
 'Mental detox is an informal phrase for taking a break or organizing worries. Negative thoughts are not toxins, and the phrase should not be confused with a clinical treatment.',
 'Therapy involves assessment and an individualized approach with a qualified professional. A self-care exercise is not a substitute when distress persists or affects daily life.',
 'You do not need to detox your mind. Leaving a practical problem unaddressed may keep it unresolved, but unwanted thoughts do not accumulate as toxins. Seek help for persistent distress.',
 ],
};
for (const [slug, replacements] of Object.entries(patches)) {
 const path = `articles/${slug}.html`;
 let html = fs.readFileSync(path, 'utf8');
 for (const [start, text] of replacements) {
  const escaped = start.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const re = new RegExp(`<p>${escaped}[^]*?</p>`, 'g');
  const found = [...html.matchAll(re)];
  if (found.length !== 1) throw new Error(`${slug}: expected one paragraph starting ${start}, got ${found.length}`);
  html = html.replace(re, `<p>${text}</p>`);
 }
 if (faqs[slug]) {
  let index = 0;
  html = html.replace(/<div class="faq-a">[^]*?<\/div>/g, () => `<div class="faq-a">${faqs[slug][index++]}</div>`);
  if (index !== 5) throw new Error(`${slug}: expected five FAQ answers`);
 }
 if (slug === 'improve-daily-routine') {
  html = html.replace(/<p>To improve daily routine, use the\s*(?=<h2>)/, '<p>To improve daily routine, use a small written plan that separates what you intend from what your schedule allows.</p><ul><li><strong>Action:</strong> Write the first task for tomorrow.</li><li><strong>Cue:</strong> Do it when you close your work document.</li><li><strong>Fallback:</strong> Write one sentence if you are interrupted.</li><li><strong>Review:</strong> Notice whether you used the note before adding another task.</li></ul><p>This is an editorial planning exercise, not a clinically validated system. Adjust it for shift work, caring responsibilities and changing health needs.</p>\n');
  html = html.replace('Why Do Most Daily Routines Fail Within Two Weeks?', 'Why Can a Daily Routine Become Difficult to Maintain?');
  html = html.replace('The strength of the anchor habit determines your success rate.', 'Choose a reminder that actually occurs in your schedule; it cannot guarantee success.');
  html = html.replace('Guilt triggers shame spirals that actually make you more likely to quit.', 'Treat a missed day as information about what needs adjusting.');
 }
 if (slug === 'how-to-detox-your-mind') html = html.replaceAll('Environmental Mental Cleansing', 'Reducing Avoidable Distractions');
 html = html.replace(/("dateModified"\s*:\s*")[^"]+"/g, '$12026-09-27"');
 fs.writeFileSync(path, html);
 console.log(`Corrected ${slug}`);
}
