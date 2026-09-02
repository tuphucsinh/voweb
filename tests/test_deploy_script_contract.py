#!/usr/bin/env python3
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

        cls.deploy_script = cls.deploy_script_path.read_text(encoding="utf-8")
        cls.staging_conf = cls.staging_conf_path.read_text(encoding="utf-8")
        cls.prod_conf = cls.prod_conf_path.read_text(encoding="utf-8")
        cls.deploy_doc = cls.deploy_doc_path.read_text(encoding="utf-8")

    def test_deploy_script_manifest_integrity(self):
        """Deploy script must verify manifest integrity but never mutate or self-write it."""
        self.assertIn('generate_release_manifest.py" --check', self.deploy_script)
        self.assertIn("sha256sum -c CHECKSUMS.sha256", self.deploy_script)
        self.assertNotIn('generate_release_manifest.py" --write', self.deploy_script)
        self.assertNotIn("--write", self.deploy_script)

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


if __name__ == "__main__":
    unittest.main()
