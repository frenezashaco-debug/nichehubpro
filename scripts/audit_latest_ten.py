"""Read-only content audit; writes report and image contact sheets only."""
import json, re, html
from pathlib import Path
from urllib.parse import urlsplit
from PIL import Image, ImageOps, ImageDraw
ROOT = Path(__file__).resolve().parents[1]
items = sorted(json.loads((ROOT/'api/articles.json').read_text(encoding='utf-8-sig')), key=lambda x:x['date'], reverse=True)[:10]
rows=[]
for item in items:
    p=ROOT/'articles'/f"{item['id']}.html"
    text=p.read_text(encoding='utf-8')
    decoded=html.unescape(text)
    plain=html.unescape(re.sub('<[^>]+>', ' ', text))
    meta=re.search(r'<meta\s+name="description"\s+content="([^"]*)"',text)
    headings=re.findall(r'<h2\b[^>]*>(.*?)</h2>',text,re.S)
    imgs=re.findall(r'<img\b[^>]*src="([^"]+)"',text)
    variants=re.findall(r'(?:src|srcset)="([^"]+)"',text)
    paths=[]
    for value in variants:
        for part in value.split(','):
            src=part.strip().split()[0] if part.strip() else ''
            if not re.search(r'\.(webp|jpg|jpeg|png)(?:\?|$)',src,re.I):continue
            path=urlsplit(src).path
            image=(ROOT/path.lstrip('/')) if path.startswith('/') else (p.parent/path).resolve()
            if image.is_file() and image not in paths:paths.append(image)
    row={**item,'em_dashes':decoded.count('\u2014'),'ai_caption':bool(re.search('Images in this article are AI-generated illustrations',decoded,re.I)), 'forbidden_phrases':re.findall(r'\bdelve\b|In today.s fast-paced world|It is important to note|In conclusion',plain,re.I),'title_has_number':bool(re.search(r'\d',item['title'])),'images':len(imgs),'faq_accordions':len(re.findall(r'class="faq-q"',text)),'meta_length':len(html.unescape(meta[1])) if meta else None,'h2':[re.sub('<[^>]+>','',h).strip() for h in headings],'tldr_label':bool(re.search(r'TL;DR\s*:',decoded,re.I)),'image_files':[str(x) for x in paths]}
    rows.append(row)
    sheet=Image.new('RGB',(1400,((len(paths)+1)//2)*420),'white');draw=ImageDraw.Draw(sheet)
    for i,image in enumerate(paths):
        x=(i%2)*700;y=(i//2)*420
        with Image.open(image) as im:sheet.paste(ImageOps.contain(im.convert('RGB'),(690,385)),(x,y))
        draw.text((x+5,y+390),image.name[:90],fill='black')
    sheet.save(ROOT/'reports'/f"latest-ten-{len(rows):02}.jpg",quality=92)
(ROOT/'reports/latest-ten-audit.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
for i,row in enumerate(rows,1):
    print(i,row['date'],row['id'],'dash',row['em_dashes'],'caption',row['ai_caption'],'images',row['images'],'FAQ',row['faq_accordions'],'meta',row['meta_length'],'number',row['title_has_number'],'TLDR',row['tldr_label'],'banned',row['forbidden_phrases'])
    print(' H2:',row['h2'])
