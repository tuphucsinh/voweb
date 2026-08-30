#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
site=json.loads((ROOT/'config/site.json').read_text())
claims=json.loads((ROOT/'content/claims.json').read_text())
prod='--production' in sys.argv
errors=[]; warnings=[]
contact=site.get('contact',{})
for key in ('email','phone','address_vi','address_en'):
    if not str(contact.get(key,'')).strip(): (errors if prod else warnings).append(f'missing contact.{key}')
launch=site.get('launch',{})
for key in ('privacy_reviewed','terms_reviewed','official_logo_confirmed','official_marigold_assets_confirmed','marigold_vietnam_claims_confirmed'):
    if not launch.get(key): (errors if prod else warnings).append(f'launch gate false: {key}')
if prod and not os.getenv('TURNSTILE_SITE_KEY'): errors.append('TURNSTILE_SITE_KEY env missing')
if prod and not os.getenv('TURNSTILE_SECRET_KEY'): errors.append('TURNSTILE_SECRET_KEY env missing')
if prod and not launch.get('production_ready'): errors.append('launch.production_ready must be true')
# Prevent accidental publish of unapproved Vietnam-market claims.
for c in claims.get('claims',[]):
    # Hidden/internal claims may be approved for record-keeping without being public-source verified.
    if c.get('approved_vn') and c.get('public_visible', True) and not c.get('verified_public'):
        errors.append(f'public claim approved_vn without verified_public: {c.get("key")}')
print('VOrigin preflight')
for w in warnings: print('WARN:',w)
for e in errors: print('ERROR:',e)
if errors:
    print(f'FAIL: {len(errors)} blocking issue(s)')
    sys.exit(2)
print('PASS')
