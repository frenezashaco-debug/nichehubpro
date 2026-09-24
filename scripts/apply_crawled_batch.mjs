import fs from 'node:fs';
import { batch, sources } from './crawled_batch_content.mjs';

const root = new URL('../', import.meta.url);
const esc = s => s.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const renderLinks = links => `<div style="background:var(--green-pale);border:1px solid var(--border);border-radius:var(--radius-sm);padding:20px 24px;margin:32px 0;"><p style="font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:var(--gray);margin-bottom:12px;">Related reading</p><ul>${links.map(([slug, label]) => `<li><a href="../articles/${slug}.html">${label}</a></li>`).join('')}</ul></div>`;
const renderFaq = faq => `<div class="faq-section" id="faq"><h2>Frequently Asked Questions</h2>${faq.map(([q,a]) => `<div class="faq-item"><button class="faq-q" aria-expanded="false"><span>${q}</span><span class="faq-icon">+</span></button><div class="faq-a" hidden>${a}</div></div>`).join('')}</div>`;
const renderSources = keys => `<div id="sources" style="margin:36px 0;padding:22px 24px;border:1px solid var(--border);border-radius:var(--radius-sm);"><h2>Sources &amp; References</h2><p>These sources provide background information. They do not diagnose or treat individual health concerns.</p><ul>${keys.map(k => `<li><a href="${sources[k][0]}">${sources[k][1]}</a></li>`).join('')}</ul></div>`;
const renderExercise = ([title, ...paragraphs]) => `<div style="background:var(--green-pale);border:1px solid var(--border);border-radius:var(--radius-sm);padding:20px 24px;margin:32px 0;"><h3>${title}</h3>${paragraphs.map(p => `<p>${p}</p>`).join('')}</div>`;

for (const [slug, data] of Object.entries(batch)) {
  const path = new URL(`articles/${slug}.html`, root);
  let html = fs.readFileSync(path, 'utf8');
  const articleStart = html.indexOf('<article class="article-content" id="article-body">');
  const articleEnd = html.indexOf('</article>', articleStart);
  if (articleStart < 0 || articleEnd < 0) throw new Error(`article boundary missing: ${slug}`);
  const body = [data.core, renderExercise(data.exercise), renderLinks(data.links), renderFaq(data.faq), renderSources(data.sources), '<p><strong>Disclaimer:</strong> This article is for informational purposes only and does not replace professional medical advice.</p>'].join('\n');
  html = html.slice(0, articleStart) + '<article class="article-content" id="article-body">\n' + body + '\n' + html.slice(articleEnd);
  html = html.replace(/<meta name="description" content="[^"]*">/i, m => m);
  html = html.replace(/<meta property="og:description" content="[^"]*">/i, m => m);
  fs.writeFileSync(path, html, 'utf8');
  console.log(`updated ${slug}`);
}
