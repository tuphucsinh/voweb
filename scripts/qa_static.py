#!/usr/bin/env python3
from pathlib import Path
from html.parser import HTMLParser
import sys, re
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'; prod='--production' in sys.argv
errors=[]; warnings=[]
DOCUMENTED_IMAGE_GEOMETRY_EXCEPTIONS=set()

def validate_image_geometry(attrs, page):
    """Return errors for local content images without positive intrinsic geometry."""
    src=attrs.get('src','')
    if not src or src.startswith(('http://','https://','//','data:')):
        return []
    if src in DOCUMENTED_IMAGE_GEOMETRY_EXCEPTIONS:
        return []
    problems=[]
    for name in ('width','height'):
        value=attrs.get(name,'')
        if not value.isdigit() or int(value)<=0:
            problems.append(f'{page}: local image {src} requires positive {name}')
    return problems

class P(HTMLParser):
    def __init__(self): super().__init__(); self.links=[]; self.imgs=[]; self.ids=set(); self.title=False; self.meta_desc=False; self.canonical=False; self.h1=0
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if 'id' in d: self.ids.add(d['id'])
        if tag=='a' and d.get('href'): self.links.append(d['href'])
        if tag=='img': self.imgs.append(d)
        if tag=='title': self.title=True
        if tag=='meta' and d.get('name')=='description' and d.get('content'): self.meta_desc=True
        if tag=='link' and d.get('rel')=='canonical': self.canonical=True
        if tag=='h1': self.h1+=1
for f in DIST.rglob('*.html'):
    p=P(); txt=f.read_text(encoding='utf-8'); p.feed(txt)
    rel=f.relative_to(DIST)
    if f.name!='404.html':
        if not p.title: errors.append(f'{rel}: missing title')
        if not p.meta_desc and rel.name!='index.html': warnings.append(f'{rel}: missing meta description')
        if f.parent!=DIST and not p.canonical: errors.append(f'{rel}: missing canonical')
        if f.parent!=DIST and p.h1!=1: errors.append(f'{rel}: expected exactly one h1, got {p.h1}')
    for img in p.imgs:
        if not img.get('alt') and img.get('alt')!='': errors.append(f'{rel}: image missing alt')
        if img.get('src','').startswith('/') and not (DIST/img['src'].lstrip('/')).exists(): errors.append(f'{rel}: missing asset {img["src"]}')
        errors.extend(validate_image_geometry(img, rel))
    for href in p.links:
        if href.startswith('/') and not href.startswith('//') and not href.startswith('/api/'):
            clean_href=href.split('#',1)[0].split('?',1)[0]
            if not clean_href: continue
            target=DIST/clean_href.lstrip('/')
            if clean_href.endswith('/'): target=target/'index.html'
            elif not target.suffix: target=target/'index.html'
            if not target.exists() and href not in ('/privacy/','/terms/'):
                errors.append(f'{rel}: broken internal link {href}')
# unsafe placeholders
for f in DIST.rglob('*.html'):
    txt=f.read_text(encoding='utf-8')
    if 'LACNOR' in txt or 'TUSCANINI' in txt or 'SUNVIEW' in txt or 'BELLAROM' in txt: errors.append(f'{f.relative_to(DIST)}: unconfirmed portfolio brand found')
    if prod and 'TURNSTILE_SITE_KEY_REQUIRED' in txt: errors.append(f'{f.relative_to(DIST)}: Turnstile placeholder found')
print(f'QA scanned {len(list(DIST.rglob("*.html")))} HTML files')
for w in warnings[:20]: print('WARN:',w)
for e in errors[:50]: print('ERROR:',e)
if errors:
    print(f'FAIL: {len(errors)} errors'); sys.exit(2)
print('PASS')
