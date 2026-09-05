#!/usr/bin/env python3
import importlib.util
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DeployScriptContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.deploy_script_path = ROOT / "scripts" / "deploy-pi5.sh"
        cls.staging_conf_path = ROOT / "ops" / "nginx" / "vorigin-staging.conf"
        cls.prod_conf_path = ROOT / "ops" / "nginx" / "vorigin.conf"
        cls.deploy_doc_path = ROOT / "DEPLOY_PI5.md"
        cls.styles_path = ROOT / "public" / "styles.css"

        cls.deploy_script = cls.deploy_script_path.read_text(encoding="utf-8")
        cls.staging_conf = cls.staging_conf_path.read_text(encoding="utf-8")
        cls.prod_conf = cls.prod_conf_path.read_text(encoding="utf-8")
        cls.deploy_doc = cls.deploy_doc_path.read_text(encoding="utf-8")
        cls.styles = cls.styles_path.read_text(encoding="utf-8")
        manifest_path = ROOT / "scripts" / "generate_release_manifest.py"
        spec = importlib.util.spec_from_file_location("generate_release_manifest", manifest_path)
        if spec is None or spec.loader is None:
            raise RuntimeError("unable to load generate_release_manifest.py")
        cls.manifest_module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.manifest_module
        spec.loader.exec_module(cls.manifest_module)

    def test_deploy_script_manifest_integrity(self):
        """Deploy script must verify manifest integrity but never mutate or self-write it."""
        self.assertIn('generate_release_manifest.py" --check', self.deploy_script)
        self.assertIn("sha256sum -c CHECKSUMS.sha256", self.deploy_script)
        self.assertNotIn('generate_release_manifest.py" --write', self.deploy_script)
        self.assertNotIn("--write", self.deploy_script)

    def test_source_manifest_ignores_preview_production_dist_difference(self):
        """Source controls must pass even when preview and production dist outputs differ."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "source.txt").write_text("same source\n", encoding="utf-8")
            dist = root / "dist"
            dist.mkdir()
            generated = dist / "index.html"
            generated.write_text('meta name="robots" content="noindex"\n', encoding="utf-8")

            first = self.manifest_module.generate_manifest(root, "write")
            self.assertFalse(first.errors)
            self.assertNotIn("dist/index.html", (root / "MANIFEST.txt").read_text(encoding="utf-8"))

            generated.write_text('meta name="robots" content="index,follow"\n', encoding="utf-8")
            second = self.manifest_module.generate_manifest(root, "check")
            self.assertFalse(second.errors)

    def test_dist_release_integrity_is_ephemeral_and_fail_closed(self):
        """Every built dist file is hashed and verified before the atomic pointer switch."""
        self.assertIn('DIST_HASHES="$(mktemp)"', self.deploy_script)
        self.assertIn('trap cleanup EXIT', self.deploy_script)
        self.assertIn('find . -type f -print0 | sort -z', self.deploy_script)
        self.assertIn('cmp -s "$DIST_FILE_LIST" "$REL_FILE_LIST"', self.deploy_script)
        self.assertIn('sha256sum -c "$DIST_HASHES"', self.deploy_script)
        verify_idx = self.deploy_script.find('if ! (cd "$REL" && sha256sum -c "$DIST_HASHES")')
        switch_idx = self.deploy_script.find('sudo ln -sfn "$REL" "$CURRENT_LINK.next"')
        self.assertGreaterEqual(verify_idx, 0)
        self.assertGreaterEqual(switch_idx, 0)
        self.assertLess(verify_idx, switch_idx)

    def test_source_validation_precedes_mode_specific_build(self):
        """Committed source controls are checked before either preview or production build."""
        manifest_idx = self.deploy_script.find('generate_release_manifest.py" --check')
        source_hash_idx = self.deploy_script.find("sha256sum -c CHECKSUMS.sha256")
        build_idx = self.deploy_script.find('python3 "$ROOT/build.py"')
        self.assertGreaterEqual(manifest_idx, 0)
        self.assertGreaterEqual(source_hash_idx, 0)
        self.assertGreaterEqual(build_idx, 0)
        self.assertLess(manifest_idx, build_idx)
        self.assertLess(source_hash_idx, build_idx)

    def test_production_turnstile_safe_default(self):
        """Production build must expand TURNSTILE_SITE_KEY with fallback to prevent set -u errors."""
        self.assertIn('TURNSTILE_SITE_KEY="${TURNSTILE_SITE_KEY:-}"', self.deploy_script)
        self.assertNotIn('TURNSTILE_SITE_KEY="$TURNSTILE_SITE_KEY"', self.deploy_script)

    def test_run_data_services_default_and_validation(self):
        """RUN_DATA_SERVICES must default to 0, validate 0/1 strictly, and gate compose execution."""
        self.assertIn('RUN_DATA_SERVICES="${RUN_DATA_SERVICES:-0}"', self.deploy_script)
        self.assertIn('if [[ "$RUN_DATA_SERVICES" != "0" && "$RUN_DATA_SERVICES" != "1" ]]', self.deploy_script)
        self.assertIn('if [[ "$RUN_DATA_SERVICES" == "1" ]]', self.deploy_script)
        self.assertIn("up -d --build db directus lead-api", self.deploy_script)

    def test_staging_rejects_shared_data_services_before_build(self):
        """Staging must reject RUN_DATA_SERVICES=1 before build or any filesystem/runtime side effect."""
        staging_reject_str = 'if [[ "$MODE" == "staging" && "$RUN_DATA_SERVICES" == "1" ]]'
        self.assertIn(staging_reject_str, self.deploy_script)
        reject_idx = self.deploy_script.find(staging_reject_str)
        build_idx = self.deploy_script.find('python3 "$ROOT/build.py"')
        self.assertNotEqual(reject_idx, -1)
        self.assertNotEqual(build_idx, -1)
        self.assertLess(reject_idx, build_idx)

    def test_production_explicit_compose_branches_without_dynamic_variable(self):
        """Production data service refresh must use explicit command branches without unquoted $COMPOSE."""
        self.assertIn('if docker compose version >/dev/null 2>&1; then', self.deploy_script)
        self.assertIn('docker compose --env-file "$ROOT/ops/.env" -f "$ROOT/ops/docker-compose.yml" up -d --build db directus lead-api', self.deploy_script)
        self.assertIn('docker-compose --env-file "$ROOT/ops/.env" -f "$ROOT/ops/docker-compose.yml" up -d --build db directus lead-api', self.deploy_script)
        self.assertNotIn('$COMPOSE', self.deploy_script)
        self.assertNotIn('COMPOSE=', self.deploy_script)

    def test_staging_and_production_isolation_boundaries(self):
        """Staging and production must use distinct roots, pointers, ports, and nginx configs."""
        # Staging isolation contract
        self.assertIn('APP_ROOT="/srv/vorigin/staging/app"', self.deploy_script)
        self.assertIn('RELEASE_ROOT="/srv/vorigin/staging/releases"', self.deploy_script)
        self.assertIn('CURRENT_LINK="/srv/vorigin/staging/current"', self.deploy_script)
        self.assertIn('NGINX_CONFIG="ops/nginx/vorigin-staging.conf"', self.deploy_script)
        self.assertIn('NGINX_SITE="vorigin-staging"', self.deploy_script)
        self.assertIn('ORIGIN_PORT="8081"', self.deploy_script)

        # Production isolation contract
        self.assertIn('APP_ROOT="/srv/vorigin/app"', self.deploy_script)
        self.assertIn('RELEASE_ROOT="/srv/vorigin/releases"', self.deploy_script)
        self.assertIn('CURRENT_LINK="/srv/vorigin/current"', self.deploy_script)
        self.assertIn('NGINX_CONFIG="ops/nginx/vorigin.conf"', self.deploy_script)
        self.assertIn('NGINX_SITE="vorigin"', self.deploy_script)
        self.assertIn('ORIGIN_PORT="8080"', self.deploy_script)

        # Dynamic variable usage for atomic pointer switch
        self.assertIn('"$CURRENT_LINK.next"', self.deploy_script)
        self.assertIn('"$CURRENT_LINK"', self.deploy_script)

    def test_staging_nginx_config_contract(self):
        """Staging Nginx config must bind to port 8081, use staging root, and never claim production hostnames or proxy leads."""
        self.assertIn("listen 127.0.0.1:8081 default_server;", self.staging_conf)
        self.assertIn("server_name staging.vorigin.vn staging.local localhost 127.0.0.1;", self.staging_conf)
        self.assertIn("root /srv/vorigin/staging/current;", self.staging_conf)
        self.assertIn("location = /healthz", self.staging_conf)

        # Production hostnames must not be declared in staging config
        self.assertNotIn("server_name www.vorigin.vn", self.staging_conf)
        self.assertNotIn("server_name vorigin.vn", self.staging_conf)
        self.assertNotIn("vorigin.vn;", self.staging_conf)

        # Forms-disabled canary must not proxy lead API
        self.assertNotIn("location /api/lead", self.staging_conf)
        self.assertNotIn("proxy_pass", self.staging_conf)

        # Security headers and denial rules must match production standards
        self.assertIn('X-Content-Type-Options "nosniff"', self.staging_conf)
        self.assertIn("Content-Security-Policy", self.staging_conf)
        self.assertIn(r"location ~* \.(?:env|ini|log|sql|bak|md|json)$", self.staging_conf)

    def test_deploy_runbook_staging_and_opt_in_documented(self):
        """DEPLOY_PI5.md must document staging port 8081 and explicit RUN_DATA_SERVICES=1 opt-in."""
        self.assertIn("http://127.0.0.1:8081/vi/", self.deploy_doc)
        self.assertIn("http://127.0.0.1:8081/healthz", self.deploy_doc)
        self.assertIn("8081", self.deploy_doc)
        self.assertIn("RUN_DATA_SERVICES", self.deploy_doc)

    def test_root_geo_contract_is_exact_and_safe_for_known_country_values(self):
        """Both Nginx sites must map only VN to VI and vary the bare-root redirect safely."""
        expected_values = {
            "VN": "vi",
            "US": "en",
            "SG": "en",
            "missing": "en",
            "XX": "en",
            "T1": "en",
            "unknown": "en",
        }
        for config in (self.prod_conf, self.staging_conf):
            map_match = re.search(
                r"map\s+\$http_cf_ipcountry\s+\$root_locale\s*\{(?P<body>.*?)\}",
                config,
                re.S,
            )
            if map_match is None:
                self.fail("missing root locale map")
            map_body = map_match.group("body")
            self.assertRegex(map_body, r"(?m)^\s*default\s+en;\s*$")
            self.assertRegex(map_body, r"(?m)^\s*VN\s+vi;\s*$")
            self.assertNotRegex(map_body, r"(?m)^\s*(?:US|SG|XX|T1|unknown)\s+vi;\s*$")
            for country, locale in expected_values.items():
                expected = "vi" if country == "VN" else "en"
                self.assertEqual(locale, expected)

            root_match = re.search(r"location\s*=\s*/\s*\{(?P<body>.*?)\n\s*\}", config, re.S)
            if root_match is None:
                self.fail("missing exact bare-root location")
            root_body = root_match.group("body")
            self.assertIn("return 302 /$root_locale/;", root_body)
            self.assertIn('add_header Cache-Control "no-store" always;', root_body)
            self.assertIn('add_header Vary "CF-IPCountry" always;', root_body)
            self.assertNotIn("return 301", root_body)

            # Geo routing must not be attached to explicit locale, asset, or health paths.
            self.assertNotRegex(config, r"location\s+[^\n]*\s/(?:vi|en)(?:/|\s)[^\n]*\{[^}]*\$root_locale", re.S)
            self.assertIn("location = /healthz", config)
            self.assertIn("location ~* \\.(?:png|jpg|jpeg|webp|avif|svg|ico)$", config)

    def test_vietnamese_display_rules_are_scoped_without_global_shrink(self):
        """VI display protections are mechanical CSS guards, not a blanket typography rewrite."""
        for selector in (
            'html[lang="vi"] .story .section-heading h2',
            'html[lang="vi"] .why-value-intro h2',
            'html[lang="vi"] .about-page .about-hero h1',
            'html[lang="vi"] .capabilities-page .page-hero h1',
        ):
            self.assertIn(selector, self.styles)
        self.assertIn("text-wrap: balance", self.styles)
        self.assertIn("word-break: normal", self.styles)
        self.assertIn("overflow-wrap: normal", self.styles)
        self.assertIn("hyphens: none", self.styles)
        self.assertNotRegex(self.styles, r'html\[lang="vi"\]\s+h2\s*\{')
        self.assertNotIn('html[lang="vi"] .standard-card h3', self.styles)

    def test_static_root_fallback_matches_global_english_default(self):
        """The static fallback must not contradict the Nginx English root default."""
        root = (ROOT / "dist" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<html lang="en">', root)
        self.assertIn('content="0;url=/en/"', root)
        self.assertIn('<a href="/vi/">Tiếng Việt</a> · <a href="/en/">English</a>', root)


if __name__ == "__main__":
    unittest.main()
