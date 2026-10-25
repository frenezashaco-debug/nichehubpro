"""Check shared article contracts without certifying scientific claims or images."""
import html,json,re
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
EXCLUDED={'how-blood-sugar-swings-affect-your-energy-and-mood','how-dopamine-actually-works-and-why-quick-fixes-backfire'}
text=(ROOT/'articles.js').read_text(encoding='utf-8')
catalog=json.loads(text[text.index('['):text.rfind(']')+1]);records={r['slug']:r for r in catalog}
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
entries={n.find('s:loc',ns).text:n.find('s:lastmod',ns).text for n in ET.parse(ROOT/'sitemap.xml').getroot() if n.find('s:lastmod',ns) is not None}
plain=lambda value:re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',value))).strip()
counts={'articles':0,'descriptions_155_to_160':0,'faq_schema_matches':0,'short_paragraph_contract':0,'preserved_local_articles':len(EXCLUDED)}
for path in sorted((ROOT/'articles').glob('*.html')):
    slug=path.stem;source=path.read_text(encoding='utf-8');counts['articles']+=1
    body=re.search(r'<article\b[^>]*>(.*?)</article>',source,re.S)[1]
    meta=html.unescape(re.search(r'<meta name="description" content="([^"]*)"',source)[1])
    assert 155<=len(meta)<=160,(slug,'meta',len(meta));counts['descriptions_155_to_160']+=1
    assert '\u2014' not in html.unescape(source),(slug,'em dash')
    assert not re.search(r'\bdelve\b',plain(body),re.I),(slug,'prohibited wording')
    documents=[json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>',source,re.S)]
    faq=next(x for x in documents if x.get('@type')=='FAQPage')
    answers=[plain(x) for x in re.findall(r'<div\b[^>]*class="faq-a"[^>]*>(.*?)</div>',body,re.S)]
    assert len(answers)==5,(slug,'FAQ count')
    assert answers==[plain(x['acceptedAnswer']['text']) for x in faq['mainEntity']],(slug,'FAQ schema')
    counts['faq_schema_matches']+=1
    if slug in EXCLUDED:continue
    h1=plain(re.search(r'<h1[^>]*>(.*?)</h1>',source,re.S)[1]);article=next(x for x in documents if x.get('@type')=='Article')
    assert h1==plain(records[slug]['title'])==plain(article['headline']),(slug,'title consistency')
    assert meta==records[slug]['excerpt']==article['description'],(slug,'description consistency')
    canonical=re.search(r'<link rel="canonical" href="([^"]+)"',source)[1]
    assert canonical=='https://nichehubpro.com/articles/'+slug+'.html',(slug,'canonical')
    assert entries[canonical]==article['dateModified'],(slug,'last modified consistency')
    for para in re.findall(r'<p\b[^>]*>(.*?)</p>',body,re.S):
        assert len(plain(para).split())<=60,(slug,'paragraph words',len(plain(para).split()))
    counts['short_paragraph_contract']+=1
print(json.dumps(counts,indent=2))
print('These checks do not verify every scientific claim, pixel watermark or AdSense eligibility.')
