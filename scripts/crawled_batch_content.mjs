// Hand-edited content for the 12 submitted URLs observed in GSC on 2026-09-24.
// Practical examples are editorial illustrations, not case reports or research.
export const sources = {
  anxiety: ['https://www.nimh.nih.gov/health/topics/anxiety-disorders', 'NIMH: Anxiety disorders'],
  relaxation: ['https://www.nccih.nih.gov/health/relaxation-techniques-what-you-need-to-know', 'NCCIH: Relaxation techniques, evidence and cautions'],
  breathing: ['https://www.nhs.uk/mental-health/self-help/guides-tools-and-activities/breathing-exercises-for-stress/', 'NHS: Breathing exercises for stress'],
  worries: ['https://www.nhs.uk/every-mind-matters/mental-wellbeing-tips/self-help-cbt-techniques/tackling-your-worries/', 'NHS: Tackling your worries'],
  burnout: ['https://www.who.int/news/item/28-05-2019-burn-out-an-occupational-phenomenon-international-classification-of-diseases', 'WHO: Burn-out as an occupational phenomenon'],
  work: ['https://www.who.int/news-room/fact-sheets/detail/mental-health-at-work', 'WHO: Mental health at work'],
  fatigue: ['https://medlineplus.gov/fatigue.html', 'MedlinePlus: Fatigue'],
  habit: ['https://doi.org/10.1002/ejsp.674', 'Lally et al. (2010): How are habits formed?'],
};
const p = text => `<p>${text}</p>`;
const list = items => `<ul>${items.map(t => `<li>${t}</li>`).join('')}</ul>`;
const section = (heading, text, items) => `<h2>${heading}</h2>${text.map(p).join('\n')}${list(items)}`;
const intro = (paragraphs, summary) => paragraphs.map(p).join('\n') + `<div class="tldr"><p>${summary}</p></div>`;
const cite = key => `<a href="${sources[key][0]}">${sources[key][1]}</a>`;

export const batch = {
  'habit-building-system': {
    sources: ['habit'],
    core: intro([
      'A habit-building system makes one intended action easier to remember, start, and review. It is not a test of whether you are disciplined enough.',
      'Perhaps you have already tried a tracker and stopped using it. Before buying another tool, look at the exact moment your plan stops fitting your day.',
      'This guide separates five design decisions: the action, cue, preparation, fallback, and review. You can change one without rebuilding your whole routine.'
    ], 'Build a habit-building system around one small action and a reliable cue. Prepare what you need, plan for interruptions, and judge the system by its usefulness rather than an unbroken streak.') +
    section('What is a habit-building system?', [
      'A system is a written arrangement for repeating a behavior. A goal such as reading more describes a direction; opening your book after lunch describes an action you can actually test.',
      `${cite('habit')} studied repeated behaviors in a consistent context and found substantial variation in the development of automaticity. It does not establish a deadline for your habit or prove this five-part worksheet will work for everyone.`,
      'Separate doing the action from getting the hoped-for result. Reading a page is observable; becoming a confident reader may take many different kinds of practice.'
    ], ['Action: what will you do?', 'Cue: what event reminds you?', 'Preparation: what must be ready?', 'Fallback: what changes on a difficult day?', 'Review: is this still useful?']) +
    section('What are the signs your plan needs adjustment?', [
      'A missed action is information about the arrangement, not evidence of a personal defect. If your cue never happens on weekends, the weekday plan needs a weekend alternative.',
      'Notice whether the obstacle is forgetting, lack of time, discomfort, or not wanting the outcome anymore. These are different problems. A reminder will not create free time, and a smaller action will not make an unwanted goal meaningful.'
    ], ['You remember only after the opportunity has passed.', 'Preparation takes longer than the action.', 'The tracker creates pressure rather than useful feedback.', 'A schedule or health change has made the original plan unrealistic.']) +
    section('Why does a habit-building system stop working?', [
      'Plans often assume more control than daily life allows. Care responsibilities, shift changes, illness, shared space, and unreliable transport can all interrupt a routine.',
      'Treat the cue as an invitation rather than a command. If you are unwell, rest may be more appropriate than preserving a streak. Avoid a system that requires ignoring pain or essential responsibilities.'
    ], ['Choose a cue that really occurs.', 'Keep materials accessible without creating a hazard.', 'Avoid attaching several new actions to one unstable event.', 'Allow the plan to change when circumstances change.']) +
    section('How do you build the five parts?', [
      '<strong>1. Specify the action.</strong> Replace learn a language with review one saved phrase. Choose a meaningful first step, not an arbitrary target selected to impress someone else.',
      '<strong>2. Choose the cue.</strong> After putting away lunch might be more reliable than exactly 12:30. If there is no stable daily event, use a calendar reminder that fits your schedule.',
      '<strong>3. Prepare the environment.</strong> Bookmark the page or place the book where you normally sit. Check whether that actually removes a barrier instead of simply moving clutter.',
      '<strong>4. Define the fallback.</strong> On a difficult day, review one phrase instead of a full lesson. A deliberate pause is also an option; it does not erase earlier practice.',
      '<strong>5. Record the obstacle.</strong> Write completed, adapted, or skipped, followed by a few words explaining why. That note is more useful for redesign than a score alone.'
    ], ['Change one component at a time.', 'Do not expand the action simply because one day went well.', 'Keep the fallback genuinely easier.', 'Use a private record if public accountability adds pressure.']) +
    section('How do you maintain the system daily?', [
      'At the cue, decide whether the usual action, fallback, or a pause fits today. At a convenient review point, ask which obstacle repeated and what can be removed.',
      'For example, if the lesson is always skipped because you cannot find headphones, prepare them. If you are consistently exhausted, reconsider the timing rather than adding louder reminders.',
      'Keep the system only while it serves a goal you still value. Stopping an unhelpful routine can be a thoughtful choice, not a failure.'
    ], ['Review patterns, not just streak length.', 'Preserve sleep and necessary care.', 'Retire tools that take more effort than they save.']),
    exercise: ['Your five-field habit card', 'Action: read one page. Cue: after putting away lunch. Preparation: book beside the usual chair. Fallback: read one paragraph or pause if needed. Review: did the location and timing help?', 'Copy these five labels into a note and fill them for your own goal. At the next review, change the field that caused the most friction, not every field at once.'],
    links: [['improve-daily-routine','adjust a routine around real constraints'], ['success-habits','choose habits that serve a specific goal'], ['how-to-focus-better-at-work','make the next work action clearer']],
    faq: [
      ['How long does a habit take to form?', 'There is no universal deadline. The behavior, context, and person matter. Review whether the action is becoming easier to start without treating a fixed number of days as a promise.'],
      ['Do I need a habit tracker?', 'No. A brief note or calendar can be enough. Use a tracker only if its feedback helps you adjust the plan.'],
      ['What if I miss several days?', 'Identify the obstacle and decide whether to restart, shrink, reschedule, or stop the action. Missing days does not erase all previous learning.'],
      ['Can I build several habits together?', 'You can, but troubleshooting becomes harder when several things change at once. Start with one if your schedule is already demanding.'],
      ['Does a system remove the need for motivation?', 'No. A system can reduce practical friction, but energy, interest, health, and circumstances still affect what you can do.']
    ]
  },
  'how-to-relax-your-mind': {
    sources: ['relaxation','breathing'],
    core: intro([
      'Learning how to relax your mind can begin with a quieter transition, not an empty mind. You may still have worries while giving yourself a little less to do.',
      'This guide is for an ordinary wind-down when you are safe but mentally busy. It is different from handling an emergency or treating an anxiety disorder.',
      'Choose one comfortable option below. Nothing here requires breath holding, enduring discomfort, or reaching a calm feeling by a deadline.'
    ], 'To relax your mind, reduce one avoidable demand and try a comfortable breathing, muscle-release, sensory, or writing exercise. Stop or change methods if discomfort increases; relaxation is optional support, not a substitute for care.') +
    section('What is mental relaxation?', [
      'For this guide, relaxation means making room to rest without requiring your thoughts to disappear. It is not proof that a medical condition has improved.',
      `${cite('relaxation')} describes several practices and explains that evidence differs by technique and condition. Some people experience increased anxiety or other discomfort, so a practice should be adapted or stopped when needed.`,
      'You do not need equipment to experiment. Pick a setting where sitting, standing, or changing position feels comfortable and where you are not responsible for driving or another safety-critical task.'
    ], ['Rest does not require silence.', 'Distraction is not automatically bad.', 'A technique can be unsuitable even if someone else likes it.']) +
    section('What are the signs you need a quieter transition?', [
      'You might notice yourself rereading a message, clenching your jaw, or carrying work conversations into the evening. Those observations can prompt a break, but they are not a diagnosis.',
      'If new physical symptoms are severe or alarming, seek medical help rather than assuming they are stress. Persistent difficulty sleeping or functioning also deserves professional advice.'
    ], ['Notice what you are doing rather than scoring yourself.', 'Pause one optional input such as a non-urgent alert.', 'Check whether you need food, rest, practical help, or a conversation instead of another exercise.']) +
    section('Why can relaxing feel difficult?', [
      'Stopping activity can leave more room to notice unfinished concerns. That does not mean you are doing relaxation incorrectly or that your brain needs to be reset.',
      'A real problem may need a practical plan. Before starting, write the next action for one unfinished task, then choose a point at which you will return to it. Do not use relaxation to avoid an urgent responsibility or unsafe situation.'
    ], ['Choose a brief, realistic stopping point.', 'Use an eyes-open option if closing your eyes is uncomfortable.', 'Let the setting and activity change if stillness is not helpful.']) +
    section('How can you try five gentle relaxation options?', [
      `<strong>1. Comfortable breathing.</strong> ${cite('breathing')} recommends gentle breathing without forcing it. Use an easy pace; there is no need to reach a particular count. If you feel dizzy or more distressed, stop the exercise and breathe normally.`,
      '<strong>2. Release unnecessary tension.</strong> Notice whether you can rest your hands or let your shoulders settle. Avoid forceful muscle tensing, painful movements, or repeatedly checking whether every muscle is relaxed.',
      '<strong>3. Look outward.</strong> Choose an ordinary object and describe its color, shape, and texture. You can stay seated with your eyes open. This is an attention exercise, not a test of how quickly anxiety falls.',
      '<strong>4. Write a closing note.</strong> Use three lines: what is unfinished, what can wait, and the next practical step. Close the note afterward rather than rewriting the worry until it feels perfect.',
      '<strong>5. Make a low-demand transition.</strong> Try a familiar piece of music, sitting near a window, or a comfortable change of position. Choose what fits your sensory preferences and surroundings.'
    ], ['Try one option, not all five in a required sequence.', 'Stop when an exercise increases distress.', 'A neutral result is useful feedback, not a failure.']) +
    section('How can relaxation fit into daily life?', [
      'Attach a short pause to a transition you already have, such as finishing work or clearing dinner. Do not take time away from sleep to complete a relaxation routine.',
      'At the end, ask whether the activity was comfortable and whether it helped you move into the next part of the day. You do not need to measure your heart rate or monitor every thought.',
      'If quiet exercises repeatedly feel frightening or bring up distressing memories, seek individualized guidance. A professional can help you find an approach suited to your circumstances.'
    ], ['Protect the option to skip.', 'Keep the practice simple enough to remember.', 'Choose support rather than longer sessions when distress persists.']),
    exercise: ['A closing note for a busy evening', 'Unfinished: I have not replied to the project email. Next step: check the deadline tomorrow before drafting a response. For now: close the work tab and prepare dinner.', 'This is an editorial example, not a treatment protocol. Replace the work task with your own concern and use the note only if it reduces repeated planning.'],
    links: [['how-to-calm-your-mind-instantly','choose a next step during acute overwhelm'], ['how-to-control-your-thoughts','respond to recurring thoughts without demanding silence'], ['how-to-deal-with-anxiety-daily','plan support for anxiety that keeps returning']],
    faq: [
      ['Do I have to meditate to relax?', 'No. A comfortable activity or a brief transition can be an alternative. Choose an option that feels accessible rather than forcing stillness.'],
      ['How quickly should I feel calmer?', 'There is no required speed or guaranteed change. If the practice is uncomfortable, stop or switch rather than increasing the effort.'],
      ['Should I hold my breath?', 'Not for the gentle practice described here. Keep breathing comfortable and unforced; stop if you become dizzy or distressed.'],
      ['Why do I feel worse when I sit quietly?', 'Experiences differ. Quiet can make worries more noticeable, and some practices are uncomfortable for some people. Try an eyes-open activity and seek guidance if this persists.'],
      ['Can relaxation replace anxiety treatment?', 'No. It can be optional support, but persistent or disabling anxiety should be assessed by a qualified professional.']
    ]
  },
  'success-habits': {
    sources: ['habit'],
    core: intro([
      'Success habits are useful only when you know what success means for you. Finishing a course, meeting an agreed deadline, or having time for family require different choices.',
      'Copying a wealthy person\'s morning does not reproduce their resources, health, responsibilities, or opportunities. A routine is one influence on an outcome, not the whole explanation.',
      'Use these seven options to support one chosen goal. This is an editorial planning guide, not a study of high achievers or a promise of financial success.'
    ], 'Choose success habits by the obstacle they address, not by celebrity routines. Define one outcome, choose a repeatable action, protect essential rest, and review whether the action helps.') +
    section('What makes a habit useful for your goal?', [
      'A useful habit connects an action you control with progress you care about. Reading a chapter might support a course; checking a tracker repeatedly may not.',
      `${cite('habit')} concerns how repetition and context relate to automaticity. It does not show that a particular morning routine causes wealth, career advancement, or personal fulfilment.`,
      'Write the outcome in plain language and name the constraint. If the constraint is unpaid care work or an unrealistic workload, better planning may be insufficient without practical support.'
    ], ['Outcome: what would be different?', 'Action: what can you reasonably do?', 'Constraint: what is outside your control?']) +
    section('What are the signs a routine is not helping?', [
      'A full calendar can hide a mismatch between effort and purpose. Look for activities you repeat because they look productive, even though they do not address your next task.',
      'Do not interpret exhaustion as proof that your habits are wrong. Health, sleep, workload, and circumstances also matter. Reduce the burden before adding another routine.'
    ], ['The routine crowds out sleep or care.', 'You track activity but cannot describe its purpose.', 'You keep adding tools rather than completing a next step.', 'The plan assumes free time you do not have.']) +
    section('Why do copied success routines disappoint?', [
      'A routine is designed inside a particular life. Advice to work before everyone wakes may not fit night work, a sleep disorder, or a young child. You do not need an early alarm to be serious about a goal.',
      'The relevant question is not what an admired person does. It is which part of your own process needs attention and what change is feasible.'
    ], ['Adapt timing to your responsibilities.', 'Distinguish an anecdote from evidence.', 'Keep limits visible when comparing your progress with someone else.']) +
    section('Which seven success habits can you test?', [
      '<strong>1. Name a deliverable.</strong> Before starting, write what finished means for this session, such as a rough outline rather than work on the project.',
      '<strong>2. Prepare the first step.</strong> Open the relevant document or collect the materials you need. Do not spend the whole session designing a workspace.',
      '<strong>3. Protect a realistic work interval.</strong> Agree on availability when your role permits. Keep a route for genuinely urgent requests.',
      '<strong>4. Learn for the current problem.</strong> Choose a lesson or reference that answers a specific question. Apply one idea before collecting more resources.',
      '<strong>5. Ask for usable feedback.</strong> Show a draft and ask what is unclear or missing. Feedback is more actionable when the question is specific.',
      '<strong>6. Leave a handoff note.</strong> Record the next action before stopping. This can make resuming simpler without requiring you to remember every detail.',
      '<strong>7. Review the trade-off.</strong> Ask what the routine costs in time, money, rest, and attention. Drop or adapt practices that no longer justify that cost.'
    ], ['Choose one option initially.', 'Measure a relevant output rather than hours alone.', 'Treat rest as a need, not a reward for perfect productivity.']) +
    section('How do you maintain progress when life changes?', [
      'Define a smaller version of the action for a constrained day, and also define when you will pause it. A smaller step is an option, not a duty to work through illness.',
      'If a deadline becomes unrealistic, discuss scope or timing early. A habit cannot replace that conversation. If resources are limited, choose the most valuable part rather than blaming yourself for not doing everything.',
      'At a review, keep a practice only if it still supports your chosen direction. A changed goal can justify a changed routine.'
    ], ['Renegotiate unrealistic commitments.', 'Resume without trying to repay every missed session.', 'Recognize progress that is not visible on a public scoreboard.']),
    exercise: ['A goal-to-action check', 'Goal: submit a course assignment. Current obstacle: the question is unclear. Useful action: ask the tutor to clarify the brief. Less useful action: spend another evening choosing a note-taking app.', 'Before adding a habit, complete this sentence: This action helps because it removes ____. If you cannot fill the gap, reconsider whether you need the habit.'],
    links: [['habit-building-system','design a cue and fallback for one action'], ['improve-daily-routine','fit the action into your actual day'], ['how-to-focus-better-at-work','protect a realistic work interval']],
    faq: [
      ['Do successful people all share the same habits?', 'No universal list explains success. Resources, opportunity, health, and context matter alongside actions. Choose habits that fit your own goal.'],
      ['Must I wake up early?', 'No. Choose a time compatible with sufficient sleep and your responsibilities. An early alarm is not evidence of a better plan.'],
      ['How many habits should I start?', 'One is a useful starting point when you want to see what helps. Add another only if the first is manageable and the new action has a clear purpose.'],
      ['What should I measure?', 'Choose an output connected to your goal and the cost of producing it. Completing a useful draft may matter more than accumulating hours.'],
      ['What if a routine stops helping?', 'Adapt it or stop it. A routine is a tool, not a commitment to repeat an unhelpful activity forever.']
    ]
  },
  'how-to-recover-from-emotional-burnout': {
    sources: ['burnout','work'],
    core: intro([
      'How to recover from emotional burnout starts with taking exhaustion seriously, not assigning yourself another demanding improvement plan.',
      'People use emotional burnout to describe many kinds of depletion. That informal phrase is broader than the occupational definition used by the World Health Organization.',
      'This guide focuses on reducing demands and preparing for support. It cannot diagnose the cause of exhaustion or tell you how many months recovery will take.'
    ], 'Start by identifying an unsustainable demand and a realistic source of support. Workload changes, rest, and professional assessment may all matter; there is no fixed recovery timetable.') +
    section('What does burnout mean here?', [
      `${cite('burnout')} defines burnout in relation to chronic workplace stress that has not been successfully managed. It is an occupational phenomenon, not a medical diagnosis that explains every form of exhaustion.`,
      'Outside work, emotional depletion is still worth taking seriously. Tell a clinician what you are experiencing rather than relying on the label to explain it. Sleep problems, mood changes, medicines, and physical illness can also need assessment.'
    ], ['Describe your symptoms in ordinary words.', 'Separate workplace demands from other pressures.', 'Avoid using a checklist to rule out another condition.']) +
    section('What signs deserve attention?', [
      'Notice changes in how you function: tasks becoming difficult, withdrawing from activities, or struggling to recover between demands. No particular number of signs confirms burnout.',
      'If you feel unable to keep yourself safe, seek urgent local help. New severe physical symptoms also need medical attention rather than being attributed to stress.'
    ], ['Record when the problem started.', 'Note the responsibilities it is affecting.', 'Include changes in sleep, mood, and physical symptoms.', 'Ask for assessment when difficulties persist or worsen.']) +
    section('Why might rest alone be insufficient?', [
      'A short break does not change an excessive workload, harassment, or lack of control over tasks. Returning to the same demands can leave the practical problem unresolved.',
      `${cite('work')} identifies workplace conditions as mental-health risks and describes organizational responses. This is not solely an individual resilience problem; consider who has the authority to change the demands.`,
      'Not everyone can safely refuse work or leave a job. Advice needs to account for income, immigration status, care duties, and the risk of retaliation. Seek confidential support when a direct conversation is not safe.'
    ], ['Identify what can be reduced or delayed.', 'Distinguish your decisions from those requiring a manager or other support.', 'Do not make a major employment decision solely from this article.']) +
    section('How can you take five practical next steps?', [
      '<strong>1. Name the demand.</strong> Replace everything is too much with a concrete example, such as three overlapping deadlines or being contacted during agreed time off.',
      '<strong>2. Request a specific change.</strong> Ask which task should take priority, whether a deadline can move, or who can share a responsibility. A defined request is easier to discuss than a general promise to cope better.',
      '<strong>3. Protect essential care.</strong> Keep room for meals, sleep, and necessary appointments. Do not turn rest into a strict routine you can fail.',
      '<strong>4. Arrange assessment or support.</strong> A qualified clinician can help evaluate ongoing symptoms. Depending on your situation, occupational health, a worker representative, or a trusted support person may help with practical barriers.',
      '<strong>5. Review the actual change.</strong> Check whether the demand was reduced, not just whether you tolerated it for another week. If nothing changed, decide who else can help.'
    ], ['Keep requests concrete and realistic.', 'Do not stop medication based on a self-help plan.', 'Use safe communication channels for sensitive workplace concerns.']) +
    section('How can you manage the process day to day?', [
      'Keep a short record of demands, functioning, and agreed changes. You do not need to rate every feeling or track yourself continuously.',
      'A return to a difficult day does not prove the plan failed. Look at whether support is available and whether the underlying conditions are changing. Discuss worsening symptoms rather than waiting for a promised recovery date.',
      'Recovery is not a competition to resume the old workload. The aim is a sustainable arrangement that respects your health and responsibilities.'
    ], ['Review commitments before adding new ones.', 'Prepare a fallback for an unusually demanding day.', 'Seek further help if functioning continues to decline.']),
    exercise: ['Prepare one workload conversation', 'Observation: Two urgent tasks now share Friday\'s deadline. Impact: I cannot complete both within agreed hours. Request: Which takes priority, and can the other move or be reassigned?', 'Adapt this script to your role. If raising the issue directly could put you at risk, seek confidential advice from an appropriate support service first.'],
    links: [['how-to-focus-better-at-work','separate task friction from excessive workload'], ['why-you-feel-tired-all-the-time','prepare questions about persistent fatigue'], ['how-to-deal-with-anxiety-daily','build a manageable anxiety support plan']],
    faq: [
      ['How long does recovery take?', 'There is no reliable timetable for everyone. The causes, health concerns, available support, and changes to demands all matter.'],
      ['Is emotional burnout a medical diagnosis?', 'The phrase is often used informally. WHO describes burnout specifically as an occupational phenomenon. A clinician can assess symptoms that may have other explanations.'],
      ['Will a vacation solve it?', 'Time away may provide rest, but it does not necessarily change the demands you return to. Consider what needs to change alongside taking a break.'],
      ['Should I quit my job?', 'That is a major personal decision. Consider health, safety, finances, available adjustments, and qualified advice rather than using a blog as the deciding factor.'],
      ['When should I seek professional help?', 'Seek help when symptoms persist, worsen, or affect daily functioning. If you cannot stay safe or symptoms are urgent, use local emergency or crisis services.']
    ]
  },
  'signs-of-anxiety-disorder': {
    sources: ['anxiety'],
    core: intro([
      'Signs of anxiety disorder can overlap with ordinary stress and other health concerns. A racing heart or a difficult night does not establish a diagnosis.',
      'What matters is the pattern, how much distress it causes, and what it prevents you from doing. You do not have to reach a symptom score before asking for help.',
      'Use this guide to prepare a conversation with a qualified professional. It is not a screening test and cannot tell you whether physical symptoms are caused by anxiety.'
    ], 'Persistent fear or worry, avoidance, sleep disruption, and physical symptoms can be reasons to seek assessment. Do not diagnose anxiety from a symptom count or assume new physical symptoms are harmless.') +
    section('What is the difference between anxiety and an anxiety disorder?', [
      `${cite('anxiety')} distinguishes occasional worry from anxiety disorders that can persist and interfere with daily activities. There are different disorders, so one checklist cannot describe every presentation.`,
      'A clinician considers your history and symptoms in context. You can ask for help even if you are uncertain what to call the problem or have not experienced it for a particular number of weeks.'
    ], ['Describe the difficulty rather than choosing a diagnosis.', 'Explain what has changed from your usual functioning.', 'Include practical pressures and health concerns.']) +
    section('What physical signs should you discuss?', [
      'People may report muscle tension, disrupted sleep, stomach discomfort, or a racing heart alongside anxiety. Similar symptoms can have other causes and deserve appropriate assessment.',
      '<strong>Do not label new chest pain, fainting, or severe breathing difficulty as anxiety.</strong> Seek urgent medical help when symptoms are severe, sudden, or feel life-threatening.'],
      ['Describe the symptom and when it occurs.', 'Mention medicines, supplements, and substance use accurately.', 'Avoid using the number of symptoms as a diagnostic threshold.']) +
    section('Why does the effect on daily life matter?', [
      'A useful question is what has become harder or unavailable to you. You might be avoiding a necessary call, struggling to complete work, or needing repeated reassurance before ordinary decisions.',
      'Avoidance has many possible explanations, including real safety concerns. Do not force yourself into a risky situation to prove you can tolerate anxiety. A professional can help decide whether a gradual plan is appropriate.',
      'Sleep difficulties also have several possible causes. Bring them into the assessment rather than assuming anxiety is the only explanation or changing prescribed treatment yourself.'
    ], ['Name one activity you have stopped or changed.', 'Explain whether the situation presents a real external risk.', 'Mention repeated checking or reassurance if it is consuming time.', 'Include sleep and concentration concerns.']) +
    section('How can you prepare to ask for help?', [
      '<strong>1. Write your main concern.</strong> A sentence such as I keep avoiding calls because I feel frightened is enough to start.',
      '<strong>2. Add a concrete example.</strong> Describe a recent occasion and its impact, not every anxious thought you have ever had.',
      '<strong>3. List relevant health information.</strong> Include sleep changes, physical symptoms, medicines, and anything you think could affect the pattern.',
      '<strong>4. Ask about options.</strong> Request an explanation of the assessment and possible support, including what to do while waiting.',
      '<strong>5. Agree on follow-up.</strong> Ask whom to contact if symptoms worsen or the suggested approach does not help. You are allowed to ask questions when advice is unclear.'
    ], ['Bring notes if speaking feels difficult.', 'Ask about accessibility, language, or cost barriers.', 'Do not wait for perfect certainty before booking an appointment.']) +
    section('How can you support yourself while waiting?', [
      'Keep the plan manageable. A trusted person, a quieter transition between activities, or practical help with a stressful task may be more useful than attempting a complete lifestyle overhaul.',
      'Self-help is optional support, not evidence that you should be able to manage without care. If an exercise makes you feel worse, stop and explain that when seeking advice.',
      'If you have immediate safety concerns or might act on thoughts of harming yourself or someone else, contact local emergency or crisis support now.'
    ], ['Keep necessary appointments and prescribed care.', 'Choose one manageable support rather than a long checklist.', 'Escalate urgent symptoms instead of waiting for a routine appointment.']),
    exercise: ['A short appointment note', 'Main concern: I avoid meetings because I worry about becoming visibly anxious. Impact: I have missed two necessary conversations. Questions: What else could explain this, and what support is appropriate?', 'This fictional note illustrates how to describe functioning. Replace it with your own experience; do not use it as a symptom test or a script for obtaining a particular diagnosis.'],
    links: [['how-to-deal-with-anxiety-daily','consider day-to-day support while seeking care'], ['how-to-control-your-thoughts','respond to distressing thoughts without self-diagnosis'], ['why-you-feel-tired-all-the-time','discuss fatigue that accompanies your symptoms']],
    faq: [
      ['How many symptoms mean I have an anxiety disorder?', 'There is no symptom count in this article that establishes a diagnosis. A qualified professional assesses the pattern, context, and impact.'],
      ['Can anxiety cause physical symptoms?', 'It can, but similar symptoms have other causes. New, severe, or concerning symptoms need medical assessment rather than an assumption.'],
      ['Must I wait until anxiety is severe?', 'No. You can seek advice when worry or fear is troubling you or interfering with activities, even if you are unsure what to call it.'],
      ['Should I stop medication and try self-help?', 'Do not stop or change prescribed medication based on this guide. Discuss questions or side effects with the prescriber.'],
      ['What should I bring to an appointment?', 'Brief notes about when symptoms began, their impact, sleep, physical symptoms, medicines, and your main questions can help structure the discussion.']
    ]
  },
  'how-to-calm-your-mind-instantly': {
    sources: ['breathing','relaxation','anxiety'],
    core: intro([
      'Wanting to calm your mind instantly is understandable when everything feels too much. No technique can promise an immediate switch from panic to calm.',
      'A more useful first aim is choosing the next safe action. You do not have to feel completely settled before asking for help or stepping away from an avoidable demand.',
      'The seven options below are alternatives, not a sequence you must finish. Skip anything that increases discomfort.'
    ], 'You cannot guarantee instant calm. Check safety first, reduce one demand, and choose a comfortable attention or breathing exercise; seek urgent help for severe physical symptoms or immediate danger.') +
    section('What is a realistic goal during overwhelm?', [
      'The aim is enough space to choose what to do next, not a perfectly calm body. You may still feel upset after making a useful decision.',
      'If you are in danger, move toward safety or assistance rather than trying to convince yourself that everything is fine. If you are driving or operating equipment, address that safety responsibility first.'
    ], ['Check your surroundings.', 'Identify whether immediate help is needed.', 'Do not use a calming exercise to dismiss a real threat.']) +
    section('What signs mean you should seek help instead?', [
      'New chest pain, fainting, or severe difficulty breathing should not automatically be treated as anxiety. Seek urgent medical help when symptoms are severe or feel life-threatening.',
      'If you may harm yourself or someone else, contact local emergency or crisis support. For recurring episodes that disrupt life, arrange professional assessment even if an exercise sometimes helps.'
    ], ['Urgent symptoms take priority over self-help.', 'A familiar label does not rule out a new problem.', 'Ask someone nearby for assistance when needed.']) +
    section('Why might a calming technique not help?', [
      'Different activities suit different people and situations. Not feeling better is not proof that you failed, practiced too little, or have a broken nervous system.',
      `${cite('relaxation')} notes that relaxation practices can sometimes bring discomfort or increased anxiety. Treat that response as a reason to stop or adapt, not push harder.`
    ], ['Choose an eyes-open option if internal focus is uncomfortable.', 'Avoid forceful breathing and breath holding.', 'Use practical support when the stressor needs a practical response.']) +
    section('How can you choose among seven immediate options?', [
      `<strong>1. Let breathing stay comfortable.</strong> ${cite('breathing')} describes gentle, unforced breathing. You do not need a long exhale or a fixed count, and you can stop if it feels uncomfortable.`,
      '<strong>2. Name a visible object.</strong> Describe its color and shape. This gives attention a simple external task without claiming to reset a nerve or hormone.',
      '<strong>3. Notice physical support.</strong> Feel the chair beneath you or your feet on the floor, if comfortable. There is no required number of sensations to identify.',
      '<strong>4. Reduce one input.</strong> Pause a non-urgent alert or close a demanding screen. Keep access to necessary communication and assistance.',
      '<strong>5. Choose a believable phrase.</strong> Try I can ask for help with the next step. Avoid I am safe if you are not actually safe.',
      '<strong>6. Change position gently.</strong> Sit, stand, or move to a quieter place if accessible and safe. You do not need vigorous exercise or cold exposure.',
      '<strong>7. Contact a person.</strong> Ask for something concrete: Can you stay with me while I decide what to do? The request can be brief.'
    ], ['Pick one option.', 'Notice comfort, not a stopwatch.', 'If it is not helping, stop and choose support.']) +
    section('How can you prepare for another difficult moment?', [
      'When you are not overwhelmed, write a short note containing a tolerable option, a person to contact, and situations that need medical help. Keep it somewhere easy to access.',
      'Do not repeatedly test yourself to prove that the technique works. If episodes keep occurring, bring the pattern to a qualified professional. '+cite('anxiety')+' provides an overview of anxiety disorders and routes to support.',
      'Your plan can change. A technique that helps on one occasion may be unhelpful on another, and practical assistance may be the better choice.'
    ], ['Keep the note short.', 'Include a way to ask for help.', 'Do not delay care while trying every technique.']),
    exercise: ['Make a next-step card', 'My comfortable option: describe an object with my eyes open. My practical request: ask someone to stay nearby. My escalation rule: seek urgent help for severe new physical symptoms or immediate danger.', 'Choose wording you can use when thinking is difficult. The card is a reminder, not a treatment protocol or a promise to stop an episode.'],
    links: [['how-to-relax-your-mind','plan a lower-pressure wind-down'], ['signs-of-anxiety-disorder','prepare for an anxiety assessment'], ['how-to-deal-with-anxiety-daily','manage recurring concerns day to day']],
    faq: [
      ['Can I guarantee calm in a minute?', 'No. A brief exercise may be useful, neutral, or uncomfortable. Aim for a safe next step rather than a guaranteed change in feeling.'],
      ['Is one breathing pattern fastest?', 'This guide does not rank techniques by speed. Comfortable, unforced breathing is an option, not a requirement.'],
      ['Should I use ice or cold water?', 'Cold exposure is not needed for the options here. Choose a comfortable external attention exercise instead of seeking a strong physical shock.'],
      ['What if breathing makes me more anxious?', 'Stop the exercise and breathe normally. Try looking at an object or asking someone for support; seek professional guidance for persistent difficulties.'],
      ['When is this not enough?', 'Recurring or disabling episodes need assessment. Immediate danger or severe physical symptoms require urgent help rather than another self-help exercise.']
    ]
  }
};
