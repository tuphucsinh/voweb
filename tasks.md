# VOweb Execution Tasks

**Plan:** `.ai/MASTER_PLAN.md` revision 7
**State:** Phase 1 foundation, P2M1T02 isolated staging, P2M1T03 production candidate and P2M1T04 apex/www public edge are verified. `admin.vorigin.vn` remains deferred Phase 3 scope.
**Rule:** Tasks below are unfinished executable work only. Mika owns verification, task status and commits; runners never edit this file, commit, push, deploy or use secrets.

## Completed foundation

- **Phase 1 / P1M1T01–P1M3T03:** `[x]` premium hardening, responsive assets, release integrity, browser matrix, lead API reliability and fail-closed preflight are complete for candidate `b9d39f92cc16c02a1e8e095d2a1455123db6ceed`.
- Evidence: `.ai/PHASE1_EXIT_REVIEW.md`, Git history and current release gates. Do not duplicate the completed task specifications here.

---

## Phase 2: Deployment-first public static launch

### [#P2M1T02] [staging runtime, Nginx, deployment wrapper] `run_isolated_canary_and_verify_boundary()`

**Goal:** Prove that the committed staging path can run locally without changing the production release, production Nginx site or shared data services.

**Depends on:** Phase 1 foundation; source boundary is committed in `b9d39f92cc16c02a1e8e095d2a1455123db6ceed`.

**Parallel-safe:** `no`

**Status:** `[x] VERIFIED — staging canary and production-boundary read-back passed 2026-09-02]`

**Evidence:** Release `/srv/vorigin/staging/releases/20260902T070832Z-staging`; Nginx `127.0.0.1:8081`; `RUN_DATA_SERVICES=0`; browser matrix `24/24`; browser helper `4/4`; production pointer and port `8080` unchanged.

**Current facts:**
- Staging contract: `/srv/vorigin/staging/current`, `127.0.0.1:8081`, Nginx site `vorigin-staging`.
- Production contract: `/srv/vorigin/current`, `127.0.0.1:8080`, Nginx site `vorigin`.
- Cloudflare nameserver delegation and Phase 2 public DNS are verified for apex/www; `admin.vorigin.vn` remains NXDOMAIN as deferred Phase 3 scope. Staging remains strictly local on `/srv/vorigin/staging/current` and `127.0.0.1:8081` with `RUN_DATA_SERVICES=0`.

**Execution:**
1. Capture the current release pointer, active Nginx config/symlinks, listeners, Docker state, cloudflared state and disk space.
2. Obtain approval for writes under `/srv/vorigin` and Nginx reload.
3. Run `./scripts/deploy-pi5.sh staging` with the default `RUN_DATA_SERVICES=0`; never pass `RUN_DATA_SERVICES=1`.
4. Verify `sudo nginx -t`, effective config, `curl -fsS http://127.0.0.1:8081/healthz`, VI/EN routes, browser matrix and port/listener scope.
5. Read back `/srv/vorigin/current` and production Nginx site; they must be unchanged.
6. Do not change Cloudflare DNS/Tunnel/Access in this task. Public edge configuration waits for P2M1T03 production preflight PASS.

**Verify:** `sudo nginx -t`; `curl -fsS http://127.0.0.1:8081/healthz`; `python3 scripts/browser_matrix.py --base-url http://127.0.0.1:8081`; listener and production-pointer read-back.

**Definition of Done:**
- Staging serves the approved static preview at port `8081` with no data-service refresh.
- Production pointer, port `8080`, Nginx site and production services are unchanged.
- Browser, Nginx, listener and denied-path evidence is recorded without secrets.

**Rollback/stop:** Remove only the staging pointer/include and restore the prior staging Nginx state. Stop on any shared production path, unexpected listener or unexplained service change.

**Approval:** staging filesystem writes, Nginx reload and wrapper execution.

---

### [#P2M1T03] [config/site.json, build.py, dist/, MANIFEST.txt, CHECKSUMS.sha256] `prepare_exact_production_candidate()`

**Goal:** Produce an indexable production artifact bound to one reviewed commit, with production preflight and release integrity proven before public routing or cutover.

**Depends on:** `[#P2M1T02]`

**Parallel-safe:** `no`

**Status:** `[x] VERIFIED — owner-confirmed production PASS for SHA `1c1b618d6fce151f0a21623fd91e06c9e8e7ebee`; production gates were completed before this session]`

**Execution:**
1. Freeze source/status and confirm `Doc/`, `.tmp/`, `ops/.env` and private artifacts are outside release scope.
2. Obtain owner approval for static public launch, forms-disabled behavior (`contact_forms_enabled=false`) and current Privacy/Terms text.
3. Change only `config/site.json:launch.production_ready` to `true`; rebuild through `build.py`, never edit `dist/` manually.
4. Run the production preflight through the secure environment boundary without printing values:
   `set -a; source ops/.env; set +a; python3 scripts/preflight.py --production`.
5. Run production build/static/copy/optimizer QA, Python/Node tests, browser matrix, manifest generation/check and `sha256sum -c CHECKSUMS.sha256`.
6. Verify `robots.txt` is indexable, preview `noindex` is absent, forms remain disabled and VI/EN content matches approval.
7. Review scope, secret scan and `git diff --check`; create the exact launch commit only after all gates pass.

**Verify:** secure-env production preflight; `make build`; production static/copy/optimizer QA; Python/Node tests; browser matrix; manifest/checksum checks; exact SHA read-back.

**Definition of Done:**
- Production preflight is `PASS` with the secure environment loaded.
- Build, browser, manifest and checksum evidence all identify the exact launch SHA.
- No private file, secret or temporary artifact is staged; no production service is reloaded.

**Rollback/stop:** Keep the prior pushed candidate and revert the flag/generated-artifact candidate if a gate fails. Stop on any unrelated diff or preflight failure.

**Approval:** public content/legal release, `production_ready=true` and exact launch commit.

---

### [#P2M1T04] [Cloudflare, production runtime, backup/rollback] `approve_and_cut_over_production()`

**Goal:** Route the approved exact candidate through Cloudflare for apex `vorigin.vn` and `www.vorigin.vn`, publish it atomically and verify application, host, runtime, edge and rollback independently.

**Depends on:** `[#P2M1T03]`

**Parallel-safe:** `no`

**Status:** `[x] VERIFIED — public edge evidence passed 2026-09-02 for production SHA `1c1b618d6fce151f0a21623fd91e06c9e8e7ebee`]`

**Public evidence:** DNS resolved via local resolver, Cloudflare DoH and Google DoH; apex `/` returned `302`, `/vi/` and `/en/` returned `200`; `www` returned `301 Location: https://vorigin.vn/`; TLS 1.3 certificate validation and SAN match passed; 31/31 static assets loaded; five checked security headers were present; `127.0.0.1:8080` remained loopback-only. No `admin.vorigin.vn` route was created.

**Execution:**
1. Obtain cutover approval tied to the exact SHA, release path, maintenance window and rollback command.
2. Capture pre-cutover release, Nginx, listener, Docker, cloudflared, disk and recent-log baseline.
3. Configure/verify Cloudflare public routes only after production preflight PASS: apex `vorigin.vn` to `127.0.0.1:8080`, `www.vorigin.vn` to approved canonical behavior (apex or canonical redirect).
4. Run the approved backup and read back its archive listing/metadata.
5. Run the audited production deployment wrapper with data services disabled (`RUN_DATA_SERVICES=0`) unless a separate production data-service approval exists.
6. Read back `/srv/vorigin/current`, release contents, Nginx effective config, listeners, health and container state.
7. Verify external HTTPS routes (`vorigin.vn`, `www.vorigin.vn`), TLS, redirects, security headers, denied paths, no `:8080` exposure and forms-disabled behavior across viewports.
8. If a critical gate fails, stop public verification, execute only the approved rollback and re-verify all boundaries.

**Verify:** pre/post `readlink -f /srv/vorigin/current`; `sudo nginx -t`; listener/container/health read-back; public DNS/HTTPS/redirect/header checks for `vorigin.vn` and `www.vorigin.vn`; browser smoke; rollback pointer read-back.

**Definition of Done:**
- `application_state`, `host_state`, `runtime_state`, `edge_state` (apex/www) and `rollback_state` are independently `PASS`.
- Public apex serves the approved SHA; `www` follows approved canonical behavior.
- Previous release and backup remain available; no data migration or lead submission occurred.

**Rollback/stop:** Restore the verified previous release and Nginx state only through the approved command. Stop on any mismatch, missing evidence or secret exposure.

**Approval:** Cloudflare apex/www changes, backup, production deployment, service reload, public cutover and rollback.

---

## Phase 3: Post-launch lead, CMS and admin route enablement

### [#P3M1T01] [Cloudflare Access/Tunnel, Turnstile, services/lead-api/, services/directus/] `enable_admin_route_lead_and_cms_after_static_launch()`

**Goal:** Configure the secure admin route contract and enable online enquiries and CMS publishing only after the static launch is stable.

**Depends on:** `[#P2M1T04]`

**Parallel-safe:** `no`

**Status:** `[DEFERRED — static launch first; admin.vorigin.vn NXDOMAIN is intentional deferred scope]`

**Scope:**
1. Configure the admin route contract: route `admin.vorigin.vn` -> Directus `127.0.0.1:8055` through Cloudflare Tunnel + Cloudflare Access.
2. Establish least-privilege Directus roles/tokens and perform secret-safe verification without exposing credentials.
3. Configure approved Turnstile keys through secure storage (`ops/.env`).
4. Run an owner-approved real-domain fixture with exact-ID cleanup and multidimensional baseline comparison checks (verifying primary target and neighboring metrics).
5. Enable forms (`contact_forms_enabled=true`) and content sync with monitoring and rollback readiness.

**Verify:** Cloudflare Access policy and Tunnel routing for `admin.vorigin.vn`; server-side least-privilege role read-back; real-domain E2E test; exact-ID cleanup; multidimensional baseline comparison; rollback evidence.

**Constraints:** No real customer data, broad cleanup, secret exposure, schema migration or use of this task to bypass static-launch gates.

**Definition of Done:** Admin route behind Access, Directus least-privilege tokens, Turnstile integration, lead/CMS evidence, cleanup, rollback and monitoring are independently reviewed and pass.
