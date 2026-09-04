#!/usr/bin/env python3
from pathlib import Path
from html.parser import HTMLParser
import sys, re
from collections import Counter
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'; prod='--production' in sys.argv
errors=[]; warnings=[]
DOCUMENTED_IMAGE_GEOMETRY_EXCEPTIONS=set()
CANONICAL_VISUALS={
    'vi/index.html': ('hero-marigold-premium', 'marigold-featured-premium', 'logistics-container-nologo'),
    'en/index.html': ('hero-marigold-premium', 'marigold-featured-premium', 'logistics-container-nologo'),
    'vi/thuong-hieu/index.html': ('marigold-featured-premium',),
    'en/brands/index.html': ('marigold-featured-premium',),
    'vi/thuong-hieu/marigold/index.html': ('marigold-featured-premium',),
    'en/brands/marigold/index.html': ('marigold-featured-premium',),
    'vi/doi-tac/index.html': ('logistics-ship-nologo',),
    'en/partners/index.html': ('logistics-ship-nologo',),
}

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
    def __init__(self): super().__init__(); self.links=[]; self.imgs=[]; self.srcsets=[]; self.ids=[]; self.hreflangs=[]; self.og_images=[]; self.title=False; self.meta_desc=False; self.canonical=False; self.h1=0
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if d.get('id'): self.ids.append(d['id'])
        if tag=='a' and d.get('href'): self.links.append(d['href'])
        if tag=='img': self.imgs.append(d)
        if tag=='source' and d.get('srcset'): self.srcsets.append(d['srcset'])
        if tag=='title': self.title=True
        if tag=='meta' and d.get('name')=='description' and d.get('content'): self.meta_desc=True
        if tag=='meta' and d.get('property')=='og:image' and d.get('content'): self.og_images.append(d['content'])
        if tag=='link' and d.get('rel')=='canonical': self.canonical=True
        if tag=='link' and d.get('rel')=='alternate' and d.get('hreflang') and d.get('href'): self.hreflangs.append((d['hreflang'],d['href']))
        if tag=='h1': self.h1+=1

def local_target(ref):
    parsed=urlsplit(ref)
    if parsed.scheme or parsed.netloc or not parsed.path.startswith('/'):
        return None
    target=DIST/parsed.path.lstrip('/')
    if parsed.path.endswith('/'): target=target/'index.html'
    elif not target.suffix: target=target/'index.html'
    return target

def srcset_urls(value):
    return [entry.strip().split()[0] for entry in value.split(',') if entry.strip()]

def ids_for(path):
    parser=P(); parser.feed(path.read_text(encoding='utf-8'))
    return set(parser.ids)

def page_locale(rel):
    if rel.parts and rel.parts[0] in {'vi','en'}: return rel.parts[0]
    return None
for f in DIST.rglob('*.html'):
    p=P(); txt=f.read_text(encoding='utf-8'); p.feed(txt)
    rel=f.relative_to(DIST)
    required_visuals=CANONICAL_VISUALS.get(rel.as_posix(), ())
    for visual in required_visuals:
        if visual not in txt: errors.append(f'{rel}: canonical visual missing {visual}')
    if len(p.ids)!=len(set(p.ids)):
        duplicates=sorted(id_ for id_,count in Counter(p.ids).items() if count>1)
        errors.append(f'{rel}: duplicate ids {duplicates}')
    if f.name!='404.html':
        if not p.title: errors.append(f'{rel}: missing title')
        if not p.meta_desc and rel.name!='index.html': warnings.append(f'{rel}: missing meta description')
        if f.parent!=DIST and not p.canonical: errors.append(f'{rel}: missing canonical')
        if f.parent!=DIST and p.h1!=1: errors.append(f'{rel}: expected exactly one h1, got {p.h1}')
    for img in p.imgs:
        if not img.get('alt') and img.get('alt')!='': errors.append(f'{rel}: image missing alt')
        if img.get('src','').startswith('/') and not (DIST/img['src'].lstrip('/')).exists(): errors.append(f'{rel}: missing asset {img["src"]}')
        errors.extend(validate_image_geometry(img, rel))
    for srcset in p.srcsets:
        for candidate in srcset_urls(srcset):
            target=local_target(candidate)
            if target is not None and not target.exists(): errors.append(f'{rel}: missing srcset asset {candidate}')
    for image in p.og_images:
        target=local_target(image)
        if target is not None and not target.exists(): errors.append(f'{rel}: missing og:image asset {image}')
    locale=page_locale(rel)
    if locale:
        hreflang_codes={code for code,_ in p.hreflangs}
        if hreflang_codes != {'vi-VN','en','x-default'}: errors.append(f'{rel}: expected vi-VN/en/x-default hreflang set, got {sorted(hreflang_codes)}')
        for code,href in p.hreflangs:
            target=local_target(href)
            if target is not None and not target.exists(): errors.append(f'{rel}: missing hreflang target {href}')
    for href in p.links:
        if href.startswith('/') and not href.startswith('//') and not href.startswith('/api/'):
            clean_href=href.split('#',1)[0].split('?',1)[0]
            if not clean_href: continue
            target=local_target(clean_href)
            if target is None: continue
            if not target.exists() and href not in ('/privacy/','/terms/'):
                errors.append(f'{rel}: broken internal link {href}')
            elif '#' in href and target.exists() and urlsplit(href).fragment and urlsplit(href).fragment not in ids_for(target):
                errors.append(f'{rel}: broken internal fragment {href}')
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
