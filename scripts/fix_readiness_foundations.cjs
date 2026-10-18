// Scoped content/form corrections; never submits a form or modifies an account.
const fs=require('node:fs'),path=require('node:path');
const root=path.join(__dirname,'..');
const privacyBody=`<h2>Information Processed When You Use the Site</h2>
  <ul>
    <li><strong>Website requests:</strong> Our hosting and security providers process requests needed to deliver pages. These requests can include your IP address, browser information and the requested URL.</li>
    <li><strong>Optional analytics:</strong> Our shared Google Analytics script loads only after you choose Allow analytics. It helps us understand visits and page use; do not assume this data is anonymous.</li>
    <li><strong>Newsletter:</strong> When you submit a newsletter form, your email address is sent to our existing Brevo subscription service. Complete any confirmation steps shown by that service.</li>
    <li><strong>Contact messages:</strong> The contact form sends the name, email, subject and message you provide to Formspree so we can receive your inquiry. Do not include medical records, financial details or other sensitive personal information.</li>
  </ul>
  <h2>How We Use Information</h2>
  <p>We use information to deliver and protect the website, respond to inquiries, manage requested email subscriptions and understand site use when analytics is allowed.</p>
  <h2>Analytics and Your Choices</h2>
  <p>Choose Allow analytics or Decline analytics in the privacy panel. Use the Privacy choices button to change your choice later. Your choice is saved in browser local storage under <code>nhp-analytics-choice-v1</code>; it is not a newsletter subscription.</p>
  <p>Declining analytics disables collection through our shared script. It does not delete previously collected data or automatically remove existing cookies. You can also use the <a href="https://tools.google.com/dlpage/gaoptout" target="_blank" rel="noopener">Google Analytics Opt-out Browser Add-on</a>.</p>
  <p>Links from Pinterest or Medium may include campaign parameters such as <code>utm_source</code>. These identify a distribution campaign, not a named reader. They are used in traffic reporting when the analytics service is allowed and records them.</p>
  <h2>Google AdSense and Advertising</h2>
  <p>The site includes Google's AdSense script. Inclusion of that script does not mean Google has approved the site or that advertisements are currently being served.</p>
  <p>When advertising is served, Google and its advertising partners may use cookies or similar technologies, depending on the applicable consent choices and configuration. Advertising consent is separate from our optional analytics panel. That panel is not a certified advertising consent management platform.</p>
  <p>For personalized ads to visitors in the EEA, UK and Switzerland, Google requires an appropriate Google-certified consent platform integrated with the IAB Transparency and Consent Framework. Our published dashboard settings alone do not demonstrate how the message behaves for a visitor. You can also review <a href="https://www.google.com/settings/ads" target="_blank" rel="noopener">Google's advertising settings</a>.</p>
  <h2>Cookies, Local Storage and Service Providers</h2>
  <p>Your browser can store our analytics preference and, when permitted, analytics cookies. Advertising and subscription services may have their own cookies or storage. Browser settings let you review and clear stored data; clearing your preference may cause the analytics question to appear again.</p>
  <p>The site uses GitHub Pages and Cloudflare for delivery and security, Google services for fonts, optional analytics and advertising integration, Brevo for newsletter forms, and Formspree for contact submissions. Information necessary for the feature you use is processed by the relevant provider.</p>
  <p>Do not submit sensitive personal information through newsletter or contact forms. For questions about information you have already submitted, contact us using the address below and identify the relevant service without sending additional private records.</p>

  `;
for(const name of ['privacy.html','privacy/index.html']){
 const file=path.join(root,name);let h=fs.readFileSync(file,'utf8');
 const start=h.indexOf('<h2>Information We Collect</h2>')>=0?'<h2>Information We Collect</h2>':'<h2>Information Processed When You Use the Site</h2>';
 const i=h.indexOf(start),j=h.indexOf('<h2>Your Rights</h2>');if(i<0||j<i)throw Error('Privacy boundaries '+name);
 h=h.slice(0,i)+privacyBody+h.slice(j);
 h=h.replace(/Last updated: [^<]+?(?= &nbsp;)/,'Last updated: October 17, 2026');
 h=h.replace('href="contact.html"','href="/contact/"');
 fs.writeFileSync(file,h);
}
const contactForm=`<form id="contact-form" action="https://formspree.io/f/mojyklpq" method="POST" style="background:var(--white);padding:32px;border-radius:var(--radius);border:1px solid var(--border);">
    <input type="hidden" name="_subject" value="New message from NicheHubPro Contact Form">
    <div class="form-group"><label for="name">Your Name</label><input type="text" id="name" name="name" autocomplete="name" required></div>
    <div class="form-group"><label for="email">Email Address</label><input type="email" id="email" name="email" autocomplete="email" required></div>
    <div class="form-group"><label for="subject">Subject</label><select id="subject" name="subject"><option>General Question</option><option>Article Suggestion</option><option>Advertising / Partnerships</option><option>Report an Issue</option><option>Privacy Question</option></select></div>
    <div class="form-group"><label for="message">Message</label><textarea id="message" name="message" required></textarea></div>
    <p style="font-size:0.85rem;">Your message is sent through Formspree. Please do not include medical records or other sensitive personal information. Read our <a href="/privacy/">privacy policy</a>.</p>
    <button class="btn" id="contact-btn" type="submit" style="width:100%;">Send Message</button>
    <p id="contact-success" role="status" hidden>Our form service accepted your message. Thank you for contacting NicheHubPro.</p>
    <p id="contact-error" role="alert" hidden>We could not confirm your message was accepted. Please try again or <a href="mailto:contact@nichehubpro.com">email contact@nichehubpro.com</a>.</p>
  </form>`;
for(const name of ['contact.html','contact/index.html']){
 const file=path.join(root,name);let h=fs.readFileSync(file,'utf8');
 h=h.replace(/<form\b[\s\S]*?<\/form>/,contactForm);
 h=h.replace(/<script>\s*function handleContact\([\s\S]*?<\/script>/,'');
 h=h.replace(/\s*<script defer src="\/contact\.js\?v=readiness-v1"><\/script>/,'');
 h=h.replace('</body>','<script defer src="/contact.js?v=readiness-v1"></script>\n</body>');
 h=h.replace('We read every message and reply within 2 business days.','Use this form for editorial corrections, website issues and general inquiries. This is not a medical advice service.');
 h=h.replace('Reply within 2 business days','Editorial and website inquiries');
 h=h.replace('<span>contact@nichehubpro.com</span>','<a href="mailto:contact@nichehubpro.com">contact@nichehubpro.com</a>');
 fs.writeFileSync(file,h);
}
const newsletterPages=['index.html','all-articles/index.html','mental-wellness/index.html','productivity/index.html','healthy-lifestyle/index.html','category.html'];
for(const name of newsletterPages){
 const file=path.join(root,name);let h=fs.readFileSync(file,'utf8');
 h=h.replace(/<script\b[^>]*src="https:\/\/sibforms\.com\/forms\/end-form\/build\/main\.js"[^>]*><\/script>/g,'');
 h=h.replace(/<script>\s*\(function\(\)\{\s*var loaded = false;[\s\S]*?end-form\/build\/main\.js[\s\S]*?<\/script>/g,'');
 fs.writeFileSync(file,h);
}
for(const name of ['about.html','about/index.html']){
 const file=path.join(root,name);let h=fs.readFileSync(file,'utf8');
 if(!h.includes('href="/editorial-policy/"'))h=h.replace('</h1>','</h1>\n<p><a href="/editorial-policy/">Read our editorial standards and correction process</a></p>');
 fs.writeFileSync(file,h);
}
const sitemapFile=path.join(root,'sitemap.xml');let sitemap=fs.readFileSync(sitemapFile,'utf8');
sitemap=sitemap.replace(/<url>[\s\S]*?<\/url>/g,b=>['about','contact','privacy'].some(slug=>b.includes('<loc>https://nichehubpro.com/'+slug+'/</loc>'))?b.replace(/<lastmod>[^<]+<\/lastmod>/,'<lastmod>2026-10-17</lastmod>'):b);
fs.writeFileSync(sitemapFile,sitemap);
console.log('Updated contact/privacy aliases, newsletter confirmation behavior, editorial discovery and sitemap dates.');
