#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER_SALTS = {'', 'change-me', 'changeme', 'default', 'replace-me', 'replace_me'}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def validate_production_environment(
    site: dict,
    claims: dict,
    env: Mapping[str, str],
    production: bool | None = None,
    product_root: Path | None = None,
) -> list[str]:
    """Return blocking/warning issue strings without printing secrets."""
    is_production = production if production is not None else env.get('SITE_ENV') == 'production'
    issues: list[str] = []
    contact = site.get('contact', {})
    for key in ('email', 'phone', 'address'):
        if not str(contact.get(key, '')).strip():
            issues.append(f'missing contact.{key}')

    launch = site.get('launch', {})
    for key in ('privacy_reviewed', 'terms_reviewed', 'official_logo_confirmed', 'official_marigold_assets_confirmed', 'marigold_vietnam_claims_confirmed'):
        if not launch.get(key):
            issues.append(f'launch gate false: {key}')

    if is_production and bool(site.get('contact_forms_enabled', False)):
        if not env.get('TURNSTILE_SITE_KEY', '').strip():
            issues.append('TURNSTILE_SITE_KEY env missing')
        if not env.get('TURNSTILE_SECRET_KEY', '').strip():
            issues.append('TURNSTILE_SECRET_KEY env missing')
    if is_production:
        salt = env.get('IP_HASH_SALT', '').strip().lower()
        if salt in PLACEHOLDER_SALTS:
            issues.append('IP_HASH_SALT missing or placeholder')
        if not launch.get('production_ready'):
            issues.append('launch.production_ready must be true')

    for claim in claims.get('claims', []):
        if claim.get('approved_vn') and claim.get('public_visible', True) and not claim.get('verified_public'):
            issues.append(f'public claim approved_vn without verified_public: {claim.get("key")}')

    products = product_root or (ROOT / 'content' / 'products')
    legacy_claim_flag = 'vn_' + 'claims_approved'
    if products.exists():
        for product_path in sorted(products.glob('*.json')):
            product = load_json(product_path)
            if legacy_claim_flag in product:
                issues.append(f'product claim flag must be removed: {product_path.relative_to(ROOT).as_posix()}')
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description='VOrigin preview/production preflight')
    parser.add_argument('--production', action='store_true', help='treat missing gates as blocking')
    args = parser.parse_args()
    site = load_json(ROOT / 'config' / 'site.json')
    claims = load_json(ROOT / 'content' / 'claims.json')
    issues = validate_production_environment(site, claims, os.environ, production=args.production)
    print('VOrigin preflight')
    for issue in issues:
        prefix = 'ERROR' if args.production else 'WARN'
        print(f'{prefix}: {issue}')
    if args.production and issues:
        print(f'FAIL: {len(issues)} blocking issue(s)')
        return 2
    print('PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
