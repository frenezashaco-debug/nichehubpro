// One-time mechanical restoration. Run with --apply; defaults to verification.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const sharp = require('sharp');
const root = path.resolve(__dirname, '..');
const manifest = require('./article_image_batch.json');
const generated = require('./image_batch_generated.json');
const apply = process.argv.includes('--apply');
const generatedDir = process.env.NHP_GENERATED_IMAGE_DIR;
const escape = s => s.replaceAll('&', '&amp;').replaceAll('"', '&quot;');
async function asset(key) {
  const original = path.join(root, 'images', key + '.webp');
  const newSource = generated[key];
  const source = newSource ? path.join(generatedDir || '', newSource) : original;
  const optimized = path.join(root, 'images', key + '-inline-v1.webp');
  const needsCopy = !!newSource || fs.statSync(original).size >= 100000;
  const target = needsCopy ? optimized : original;
  if (needsCopy && apply && !fs.existsSync(target)) {
    assert(!newSource || generatedDir, 'Set NHP_GENERATED_IMAGE_DIR for generated assets');
    for (const quality of [80, 72, 64, 56]) {
      const buffer = await sharp(source).resize({width: 1000, withoutEnlargement: true}).webp({quality}).toBuffer();
      if (buffer.length < 100000) { fs.writeFileSync(target, buffer, {flag:'wx'}); break; }
    }
  }
  assert(fs.existsSync(target), `Missing optimized asset: ${target}`);
  assert(fs.statSync(target).size < 100000, `Asset over budget: ${target}`);
  const meta = await sharp(target).metadata();
  return {file:path.basename(target), width:meta.width, height:meta.height};
}
async function main() {
  let added=0;
  for (const [slug, alts] of Object.entries(manifest)) {
    const file = path.join(root, 'articles', slug+'.html');
    const before = fs.readFileSync(file,'utf8');
    let html=before;
    for (const [index,section] of [1,3,5].entries()) {
      const a=await asset(slug+'-sec'+section);
      const src='../images/'+a.file;
      const tag=`<img src="${src}" alt="${escape(alts[index])}" width="${a.width}" height="${a.height}" loading="lazy" decoding="async" style="width:100%;height:auto;border-radius:10px;margin:28px 0 20px;display:block;">`;
      if(!html.includes(src)) {
        assert(apply, `${slug}: missing ${src}`);
        const heading = new RegExp('<h2\\b[^>]*id="sec-'+[2,4,5][index]+'"[^>]*>');
        if(heading.test(html)) html=html.replace(heading, match=>tag+'\n'+match);
        else {
          const headings=[...html.matchAll(/<h2\b[^>]*>/g)];
          const match=headings[[1,3,4][index]];
          assert(match, `${slug}: insertion heading absent`);
          html=html.slice(0,match.index)+tag+'\n'+html.slice(match.index);
        }
        added++;
      }
    }
    if(slug==='how-to-calm-your-mind-instantly' && !new RegExp('<img\\b[^>]*src="\\.\\./images/'+slug+'\\.webp"').test(html)) {
      assert(apply, 'Missing cover');
      const meta=await sharp(path.join(root,'images',slug+'.webp')).metadata();
      html=html.replace(/(<article\b[^>]*id="article-body"[^>]*>)/, `$1\n<img src="../images/${slug}.webp" alt="Woman taking a seated pause beside a window" width="${meta.width}" height="${meta.height}" fetchpriority="high" decoding="async" style="width:100%;height:auto;border-radius:10px;display:block;margin-bottom:28px;">`);
      added++;
    }
    assert.equal((html.match(/<img\b/g)||[]).length,4,slug+': expected four images');
    if(html!==before) {
      const normalize = text=>text.replace(/<img\b[^>]*>/g,'').replace(/\s+/g,'');
      assert.equal(normalize(html),normalize(before),slug+': non-image content changed');
      fs.writeFileSync(file,html);
    }
  }
  console.log(`PASS: ${Object.keys(manifest).length} articles; ${added} image elements added; inline assets below 100 kB.`);
}
main().catch(e=>{console.error(e);process.exitCode=1;});
