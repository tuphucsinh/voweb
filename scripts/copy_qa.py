#!/usr/bin/env python3
from pathlib import Path
from html.parser import HTMLParser
import re, sys

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'

BLOCKED = [
    'world-class','seamless','unlock','elevate','transformative','cutting-edge',
    'game-changing','next-level','synergy','holistic','bespoke','reimagine','redefine',
    'empower','leverage our','our ecosystem','innovative solutions'
]
US_VISIBLE = [r'\bflavor\b', r'\bflavors\b', r'\blocalization\b', r'\blabeling\b', r'\binquiry\b']

class TextParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.skip=0
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'): self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('script','style') and self.skip: self.skip -= 1
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)

def visible_text(path: Path) -> str:
    p=TextParser(); p.feed(path.read_text(encoding='utf-8')); return ' '.join(' '.join(p.parts).split())

errors=[]
for page in list((DIST/'vi').rglob('*.html')) + list((DIST/'en').rglob('*.html')):
    text=visible_text(page)
    low=text.lower()
    for term in BLOCKED:
        if term in low:
            errors.append(f'{page.relative_to(DIST)}: blocked filler phrase: {term}')
    if '/en/' in '/' + str(page.relative_to(DIST)).replace('\\','/'):
        for pat in US_VISIBLE:
            if re.search(pat, text, flags=re.I):
                errors.append(f'{page.relative_to(DIST)}: English style mismatch: {pat}')

if errors:
    print('COPY QA FAIL')
    print('\n'.join(errors))
    sys.exit(1)
print(f'COPY QA PASS — scanned {len(list((DIST/"vi").rglob("*.html"))) + len(list((DIST/"en").rglob("*.html")))} VI/EN pages')
