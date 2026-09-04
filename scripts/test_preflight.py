#!/usr/bin/env python3
import copy
import unittest
from pathlib import Path

from preflight import load_json, validate_production_environment

ROOT = Path(__file__).resolve().parents[1]


class PreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site = load_json(ROOT / 'config' / 'site.json')
        cls.claims = load_json(ROOT / 'content' / 'claims.json')

    def test_preview_is_clean_after_owner_content_approval(self):
        issues = validate_production_environment(self.site, self.claims, {}, production=False)
        self.assertEqual(issues, [])
        self.assertNotIn('TURNSTILE_SITE_KEY env missing', issues)

    def test_production_is_fail_closed_for_unapproved_gates_and_placeholder_salt(self):
        site = copy.deepcopy(self.site)
        site['launch'].update({
            'production_ready': False,
            'privacy_reviewed': False,
            'terms_reviewed': False,
            'official_marigold_assets_confirmed': False,
        })
        issues = validate_production_environment(site, self.claims, {
            'TURNSTILE_SITE_KEY': 'fixture-site-key',
            'TURNSTILE_SECRET_KEY': 'fixture-secret-key',
            'IP_HASH_SALT': 'change-me',
        }, production=True)
        self.assertIn('launch gate false: privacy_reviewed', issues)
        self.assertIn('launch gate false: terms_reviewed', issues)
        self.assertIn('launch gate false: official_marigold_assets_confirmed', issues)
        self.assertIn('IP_HASH_SALT missing or placeholder', issues)
        self.assertIn('launch.production_ready must be true', issues)

    def test_fully_approved_fixture_has_no_issues(self):
        site = copy.deepcopy(self.site)
        site['contact_forms_enabled'] = False
        site['launch'].update({
            'production_ready': True,
            'privacy_reviewed': True,
            'terms_reviewed': True,
            'official_logo_confirmed': True,
            'official_marigold_assets_confirmed': True,
            'marigold_vietnam_claims_confirmed': True,
        })
        issues = validate_production_environment(site, self.claims, {
            'IP_HASH_SALT': 'a-realistic-fixture-salt',
        }, production=True)
        self.assertEqual(issues, [])

if __name__ == '__main__':
    unittest.main()
