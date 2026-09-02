# VOweb Master Plan

**Revision:** 3
**Last reviewed:** 2026-09-02
**Status:** Deployment-first; static public launch is the priority, but the public edge and isolated-canary gates are still blocked.
**Current candidate commit:** `ab32d1cf8863cc6c037e114c1159a1114213b095`
**Confidence:** CAO

## 1. Goal

Đưa bản VOweb static rc7 hiện tại lên public canonical domain `https://vorigin.vn` theo đường ngắn nhất an toàn, không biến commit/push hoặc `production_ready=true` thành bằng chứng deploy thành công.

### Launch outcome

- `https://vorigin.vn/vi/` and `/en/` return the intended production pages over HTTPS.
- `https://www.vorigin.vn/*` follows the approved canonical apex redirect without exposing `:8080` or downgrading to HTTP.
- Production HTML is indexable only after the exact launch candidate is approved; preview/staging remains `noindex`.
- Nginx, Docker services and Cloudflare Tunnel retain loopback/private boundaries.
- `/srv/vorigin/current` points to the exact approved timestamped release.
- A fresh backup, rollback target and post-cutover evidence exist before the public switch.
- Contact and partnership forms remain intentionally disabled for this first static launch. Turnstile, lead delivery and Directus publishing are a later phase.

## 2. Strongest pushback and optimality check

### Rejected: deploy directly now

This is not safe or verifiable at the current state:

- `vorigin.vn` and `www.vorigin.vn` currently do not resolve from this host.
- `launch.production_ready` is `false` in `config/site.json`.
- `python3 scripts/preflight.py --production` without the deployment environment fails on missing `IP_HASH_SALT` and the production flag; the secret value must remain in `ops/.env` and is never printed.
- No exact public HTTPS/DNS evidence exists for the candidate.
- No explicit production cutover approval is attached to the current SHA.

### Rejected: run the existing staging command as-is

`scripts/deploy-pi5.sh staging` currently writes `/srv/vorigin/current`, uses the same `127.0.0.1:8080` Nginx origin and reloads the same Nginx service. It is not an isolated staging path and can replace the release currently serving the origin.

### Chosen route: deployment-first static launch

1. Establish and verify the Cloudflare public edge for `vorigin.vn`/`www`.
2. Make the staging/canary path physically separate from production.
3. Prepare an exact production artifact and obtain approval tied to its SHA.
4. Run production preflight with the wrapper's environment, then atomically cut over.
5. Verify the public edge independently and keep rollback ready.
6. Enable forms, Turnstile and CMS only after the static launch is stable.

This is materially faster than the old plan because forms are already disabled, so staging Turnstile/lead submission and Directus service-token setup are not launch blockers. It is safer than a direct deploy because the public edge, artifact identity and rollback remain independently proven.

## 3. Verified starting state

### 3.1 Repository and candidate

**VERIFIED_NOW:**

- Root: `/home/pi5/projects/VOweb`
- Branch: `main`
- Local HEAD and `origin/main`: `ab32d1cf8863cc6c037e114c1159a1114213b095`
- Tracked/staged product changes: none after the pushed candidate.
- Untracked paths: `Doc/` and `.tmp/`; these remain excluded from release/commit and must not be deleted by this plan.
- `config/site.json`: `contact_forms_enabled=false`, `launch.production_ready=false`.
- `ops/.env`: exists with mode `600`; values are not read into reports.

**RECORDED_EVIDENCE_BOUND_TO_CURRENT_COMMIT:**

- Build/static/copy and preflight contract checks passed for the candidate; production preflight remains blocked while the launch flag is false or the wrapper environment is absent.
- Browser matrix recorded `24/24` route/viewport results at `390x844`, `768x1024` and `1440x900` in `/home/pi5/hermes-artifacts/browser-evidence/VOweb/commit-verify`.
- Release manifest and SHA-256 verification passed after the final candidate reconciliation.
- The numeric CDP overflow probe remains `BLOCKED_BROWSER_LAYOUT`; screenshots are not numeric overflow proof.

### 3.2 Host and runtime

**VERIFIED_NOW:**

- `nginx`: active and enabled.
- `cloudflared`: active and enabled.
- Docker services: `vorigin-db-1` is healthy; Directus and lead-api are running; Directus is published only at `127.0.0.1:8055`, lead-api only at `127.0.0.1:8787`.
- Nginx is listening at `127.0.0.1:8080`.
- `/srv/vorigin/current` is a valid symlink to `/srv/vorigin/releases/20260831T035626Z-production`.
- Existing current release is older than the candidate: hashes for `vi/index.html` and `en/index.html` differ from the repository `dist/` versions.
- `/etc/cloudflared/token` exists with mode `600`; the token value was not read.
- `vorigin-health.timer`, `vorigin-backup.timer` and `vorigin-content-sync.timer` are not installed/enabled on this host.

### 3.3 Edge

**BLOCKED_NOW:**

- `getent ahostsv4 vorigin.vn` and `www.vorigin.vn` return no address.
- HTTPS requests to both domains fail at DNS resolution.
- An active `cloudflared` process proves connector health only; it does not prove DNS or a public-hostname ingress route.

### 3.4 Source-of-truth paths

- Static generator: `build.py`
- Production gates: `scripts/preflight.py`, `scripts/test_preflight.py`
- Deployment wrapper: `scripts/deploy-pi5.sh`
- Browser verification: `scripts/browser_matrix.py`, `tests/browser-verify.sh`
- Public origin: `ops/nginx/vorigin.conf`
- Private services: `ops/docker-compose.yml`
- Edge instructions: `ops/cloudflare/README.md`
- Backup/health: `scripts/backup.sh`, `scripts/healthcheck.sh`, `ops/systemd/`
- Rollback runbook: `OPERATIONS.md`, `DEPLOY_PI5.md`

## 4. Architecture and boundaries

```text
visitor
  -> Cloudflare HTTPS/WAF
  -> Cloudflare Tunnel (outbound from Pi)
  -> Nginx 127.0.0.1:8080
  -> /srv/vorigin/current (static release)

admin.vorigin.vn
  -> Cloudflare Access
  -> 127.0.0.1:8055 Directus
  -> private Docker network -> PostgreSQL
```

- No router port-forwarding and no public database/Directus/lead-api binding.
- The first launch serves static pages with contact/partnership forms disabled.
- Do not expose `admin.vorigin.vn` without Cloudflare Access.
- Do not read, print, commit or place Cloudflare, Directus, Turnstile or env secret values in prompts/evidence.

## 5. Scope and non-goals

### In scope now

- Cloudflare DNS/public-hostname verification for `vorigin.vn` and `www.vorigin.vn`.
- Safe, physically isolated local canary path.
- Deployment-wrapper boundary needed to avoid accidental production overwrite or unrelated service restart.
- Exact production build, manifest/checksum and preflight evidence.
- Backup, atomic production cutover, public HTTPS verification and rollback readiness.
- Installation and verification of health/backup timers only when separately approved and scoped.

### Deferred until after static launch

- Turnstile widget and secret configuration.
- Enabling public lead/contact forms.
- Directus role/token creation, CMS sync and real lead delivery.
- Monitoring hostname exposure and content-sync timer.
- Lighthouse/Web Vitals optimization beyond a launch smoke baseline.

### Explicitly out of scope

- Full redesign, framework migration, database migration or schema change.
- Router/firewall port forwarding.
- Deleting old releases or `Doc/`/`.tmp/`.
- Production DNS/cutover, service reload, credential or permission changes without explicit approval.
- Inventing legal text, contact facts, claims or asset authorization.

## 6. Phase 1 — Premium hardening and release integrity

**Status:** DONE for the current candidate; technical evidence is recorded, while public launch was intentionally not performed.

The Phase 1 candidate preserves the approved visual system and includes the B2B hero cleanup, mobile fold/order fixes, responsive image contracts, safe cache behavior, deterministic release metadata, browser matrix, lead API reliability tests and fail-closed production preflight. The detailed historical task evidence remains in `.ai/PHASE1_EXIT_REVIEW.md` and the completed entries in `tasks.md`.

Phase 1 does not prove public edge readiness, production approval or a deployed release.

## 7. Phase 2 — Deployment-first public static launch

### Milestone M1 — Edge and canary boundary

#### [#P2M1T01] [config/site.json, legal content, approved assets] `close_owner_content_gates()`

**Goal:** Close only the owner-controlled content and asset gates already approved, without enabling production readiness.

**Status:** DONE. Owner-controlled facts (phone, bilingual address, legal review flags, and official MARIGOLD assets) are confirmed in `config/site.json`. `contact_forms_enabled=false` and `launch.production_ready=false` remain intentionally set for static launch.

#### [#P2M1T02] [scripts/deploy-pi5.sh, ops/nginx/vorigin-staging.conf, tests/test_deploy_script_contract.py, DEPLOY_PI5.md] `establish_edge_and_isolated_canary()`

**Goal:** Prove the public edge, enforce deployment integrity by removing manifest self-writing, make staging/canary physically unable to overwrite `/srv/vorigin/current` or production Nginx config, and make data-service refresh opt-in for production only while rejecting it in staging.

**Depends on:** `[#P2M1T01]` — complete.

**Parallel-safe:** `no`

**Concrete changes and checks:**

1. Capture a read-only baseline: current Git SHA/status, `/srv/vorigin/current` target, release directory list, active Nginx symlink/effective config, listeners, Docker status and Cloudflare service status.
2. Enforce check-only deployment integrity: remove `generate_release_manifest.py --write` from `scripts/deploy-pi5.sh` so deployment only verifies `generate_release_manifest.py --check` and `sha256sum -c CHECKSUMS.sha256` without mutating workspace integrity metadata.
3. Safe variable expansion: use `TURNSTILE_SITE_KEY="${TURNSTILE_SITE_KEY:-}"` in `scripts/deploy-pi5.sh` so absent optional keys cannot cause `set -u` failures.
4. Mode-aware deployment wrapper & isolated paths:
   - Staging: `APP_ROOT=/srv/vorigin/staging/app`, `RELEASE_ROOT=/srv/vorigin/staging/releases`, `CURRENT_LINK=/srv/vorigin/staging/current`, `NGINX_CONFIG=ops/nginx/vorigin-staging.conf`, `NGINX_SITE=vorigin-staging`, `ORIGIN_PORT=8081`.
   - Production: `APP_ROOT=/srv/vorigin/app`, `RELEASE_ROOT=/srv/vorigin/releases`, `CURRENT_LINK=/srv/vorigin/current`, `NGINX_CONFIG=ops/nginx/vorigin.conf`, `NGINX_SITE=vorigin`, `ORIGIN_PORT=8080`.
5. Dedicated staging Nginx configuration `ops/nginx/vorigin-staging.conf`: listens on `127.0.0.1:8081 default_server`, serves `/srv/vorigin/staging/current`, excludes production hostnames (`vorigin.vn`, `www.vorigin.vn`), omits `/api/lead` proxy, and preserves all production security headers and hidden/config denial rules.
6. Opt-in data services & staging fail-closed boundary: default `RUN_DATA_SERVICES="${RUN_DATA_SERVICES:-0}"` with strict `0|1` validation; staging rejects `RUN_DATA_SERVICES=1` before build or runtime side effects because the Compose stack is shared. Production-only opt-in runs explicit `docker compose` or `docker-compose` branches without dynamic unquoted command variables.
7. Contract tests: add side-effect-free `tests/test_deploy_script_contract.py` verifying manifest check-only integrity, variable expansion, staging rejection of `RUN_DATA_SERVICES=1`, explicit production Compose fallback branches, isolated roots/pointers/ports, Nginx staging config, and documentation contracts.
8. Runbook documentation: update `DEPLOY_PI5.md` to document staging port `8081`, healthz verification, staging static-only boundary rejecting shared data services, and production-only opt-in `RUN_DATA_SERVICES=1` instructions.
9. With owner-approved Cloudflare access, configure/verify:
   - `vorigin.vn` public hostname -> HTTP `127.0.0.1:8080`;
   - `www.vorigin.vn` -> the same origin or an approved edge redirect;
   - `admin.vorigin.vn` -> HTTP `127.0.0.1:8055` behind Access only.
10. Query public DNS and make safe HTTPS GET/redirect/header checks. If DNS or public-hostname ingress is absent, stop with `BLOCKED_EXTERNAL_ROUTE_CONFIGURATION`; do not inspect or mutate the tunnel token.

**Definition of Done:**

- Deployment wrapper eliminates manifest self-writing and enforces verification-only integrity.
- Staging/canary has distinct release root (`/srv/vorigin/staging/releases`), pointer (`/srv/vorigin/staging/current`), port (`8081`), and Nginx site (`vorigin-staging`); a canary deploy cannot touch `/srv/vorigin/current` or production Nginx site.
- Staging rejects `RUN_DATA_SERVICES=1` before build/runtime mutation; production allows data service refresh only when `RUN_DATA_SERVICES=1` is explicitly provided and approved.
- `python3 -m unittest tests/test_deploy_script_contract.py` passes.
- Effective Nginx behavior and loopback listener scope are evidenced.
- `vorigin.vn` and `www.vorigin.vn` resolve and the approved public route is observable, or the task remains blocked with the exact missing Cloudflare owner action.
- Existing production release pointer is unchanged by canary work.
- No secret value appears in command output/evidence.

**Rollback:** remove only the staging include/pointer and restore the prior Nginx symlink/config; production current pointer must remain untouched.

**Approval:** external Cloudflare changes, Nginx reload, filesystem writes under `/srv/vorigin` and any deployment-wrapper execution require explicit approval before execution.

### Milestone M2 — Exact launch candidate

#### [#P2M1T03] [config/site.json, build.py, dist/, MANIFEST.txt, CHECKSUMS.sha256] `prepare_exact_production_candidate()`

**Goal:** Produce a production-indexable artifact whose exact commit, generated output and preflight result are known before cutover.

**Depends on:** `[#P2M1T02]`

**Parallel-safe:** `no`

**Concrete changes and checks:**

1. Freeze the source baseline and confirm no `Doc/`/`.tmp/` material is entering the release.
2. Obtain owner approval to publish the current static release with forms disabled and to enable the production flag for the launch candidate. If the current Privacy/Terms draft notice is not approved for public use, stop and record the required final text instead.
3. Mika changes only `config/site.json` `launch.production_ready` to `true` after that approval; rebuild through `build.py`, never edit `dist/` manually.
4. Run production preflight with the same secret-safe environment boundary as the wrapper:

   ```bash
   set -a; source ops/.env; set +a
   python3 scripts/preflight.py --production
   ```

   Values from `ops/.env` must not be printed, copied into prompts or persisted in evidence.
5. Run the production build and gates: `python3 build.py`, `python3 scripts/qa_static.py --production`, `python3 scripts/copy_qa.py`, optimizer check, manifest generation/check, `sha256sum -c CHECKSUMS.sha256`, Python/Node checks and the browser matrix against an isolated local production artifact.
6. Verify `dist/robots.txt` is indexable, preview `noindex` is absent from production HTML, forms remain absent, and the generated pages match the approved VI/EN content.
7. Review `git diff`, `git diff --check`, manifest scope and secret-like paths. Create the exact launch commit only after all checks pass; the cutover approval must reference that resulting SHA.

**Definition of Done:**

- `scripts/preflight.py --production` returns `PASS` with the wrapper environment.
- Production build/static/copy/browser/manifest/checksum gates pass; exact evidence is bound to the launch SHA.
- `production_ready=true` exists only in the owner-approved launch candidate, not as a standalone readiness claim.
- No secret, private `Doc/` file or `.tmp/` artifact is staged.

**Rollback:** revert the launch-flag/generated-artifact candidate commit before cutover; keep the previous pushed candidate available.

**Approval:** owner approval for public content/flag and separate approval for creating the exact launch commit.

### Milestone M3 — Production cutover and public verification

#### [#P2M1T04] [production runtime] `approve_and_cut_over_production()`

**Goal:** Atomically publish the approved launch SHA on `vorigin.vn`, verify all four runtime boundaries, and retain a tested rollback target.

**Depends on:** `[#P2M1T03]`

**Parallel-safe:** `no`

**Concrete changes and checks:**

1. Obtain explicit cutover approval tied to the exact launch SHA, release path, maintenance window and rollback command. This is not inferred from Phase 1 or preflight PASS.
2. Capture the immediately-before baseline: current release symlink/hash, Nginx effective config, listeners, Docker status/restart counts, cloudflared status, disk space and recent startup/fatal logs.
3. Run the approved backup path before mutation. Verify the backup directory, archive listing, expected config/content/dist artifacts and backup metadata; do not claim backup success from a final log line alone.
4. Run the audited production deploy wrapper for the exact SHA. Preserve the first useful failure. Do not retry without new evidence.
5. Independently read back `/srv/vorigin/current`, release files, Nginx syntax/effective config, listeners, health endpoint, container state and logs. `Up` is not treated as native health unless the service exposes a health check.
6. Verify public edge behavior from outside the local origin boundary:
   - apex `/`, `/vi/`, `/en/`;
   - `www` redirect behavior;
   - HTTPS/TLS and security headers;
   - safe hidden/source path denials;
   - no `:8080` exposure and no HTTP downgrade.
7. Run read-only browser smoke on the exact public routes at mobile/tablet/desktop sizes. Assert forms are intentionally disabled and no Turnstile script is loaded.
8. If a critical gate fails, stop public verification, preserve raw evidence, and perform only the approved rollback to the previous release. Re-verify release pointer, Nginx, listeners, health and public edge after rollback.

**Definition of Done:**

- `application_state=PASS`, `host_state=PASS`, `runtime_state=PASS`, `edge_state=PASS` with exact evidence paths.
- Public `vorigin.vn` serves the approved launch SHA; `www` follows the approved canonical behavior.
- Previous release and rollback procedure are read back and remain available.
- No data migration, lead submission, public credential exposure or unrelated service change occurred.

**Approval:** explicit production cutover approval is mandatory immediately before execution; backup/rollback and public edge changes are separate approval boundaries.

## 8. Phase 3 — Post-launch lead and CMS enablement

**Status:** DEFERRED until the static public launch is stable.

1. Configure Turnstile only after an approved widget/domain and secret-safe runtime store exist.
2. Enable forms only after a real-domain E2E contract, owner-approved fixture, exact-ID cleanup and multidimensional baseline verification exist.
3. Configure Directus least-privilege roles/tokens and verify scopes without exposing token values.
4. Enable content sync only after draft/review/publish and rollback are tested.
5. Add external monitoring only with an approved hostname and access policy.

This phase must not block the first public static launch while forms remain disabled.

## 9. Verification contract

Report the following independently; never collapse them into one readiness boolean:

```text
application_state: PASS|FAIL|BLOCKED + command/evidence
host_state: PASS|FAIL|BLOCKED + config/listener evidence
runtime_state: PASS|FAIL|BLOCKED + process/container/health evidence
edge_state: PASS|FAIL|BLOCKED + DNS/HTTPS/redirect evidence
rollback_state: PASS|FAIL|BLOCKED + previous release/backup evidence
residual_blocker: exact owner/action or NONE
```

### Required commands by gate

- Source: `git status --short --branch`, `git rev-parse HEAD`, `git diff --check`.
- Application: `python3 build.py`, static/copy QA, `python3 scripts/preflight.py --production` with `ops/.env`, manifest/checksum checks, Node tests.
- Host: `sudo nginx -t`, `sudo nginx -T`, active-site symlink, `ss -ltnp`.
- Runtime: `docker compose --env-file ops/.env -f ops/docker-compose.yml ps --all`, `systemctl is-active`, safe health probes, restart/log inspection.
- Edge: public DNS queries, `curl -sSIL`/safe GET to exact HTTPS routes and redirect/header assertions.
- Browser: `/usr/bin/google-chrome-stable` through the project browser harness; evidence must identify the tested base URL and launch SHA.
- Rollback: previous release target, backup archive listing, approved pointer restore and post-restore read-back.

### Performance and accessibility

- Launch gate: static HTTP/HTTPS correctness, browser render, content order, asset availability and security headers.
- Lighthouse/Web Vitals: `Monitor` after the public static launch because no approved Lighthouse evidence is currently available; record a baseline against the live exact SHA before prioritizing optimization.
- Numeric layout overflow: remain `UNKNOWN/BLOCKED_BROWSER_LAYOUT` until the CDP capability is fixed; do not convert screenshots into a numeric PASS.

## 10. Risks and stop conditions

Stop immediately and preserve the first useful evidence when:

- DNS or public-hostname ingress is absent or points somewhere unexpected.
- Canary and production share a release pointer, root or port.
- `production_ready` is enabled without the owner/content approval recorded for the exact candidate.
- Production preflight fails or is run without the wrapper's environment.
- Exact launch SHA, release files or checksum manifest do not match.
- Nginx effective config differs from the reviewed source or a non-loopback service listener appears.
- Docker restart counts/logs show an unexplained regression.
- Any credential, cookie, token or private data appears in output/evidence.
- The same failure repeats twice without new operational evidence.
- Rollback target or backup cannot be read back.

## 11. Open decisions / owner actions

1. **Static-first launch approval:** confirm public launch is allowed with `contact_forms_enabled=false` and direct contact details only.
2. **Legal final-use approval:** confirm current Privacy/Terms text is approved for public use, or provide final bilingual text before enabling `production_ready`.
3. **Cloudflare edge action:** configure/confirm DNS and public hostnames for `vorigin.vn` and `www.vorigin.vn`; protect `admin.vorigin.vn` with Access.
4. **Canary/cutover approval:** approve the isolated canary host changes, exact launch SHA and production maintenance window.
5. **Monitoring decision:** choose an external uptime monitor only after the public edge is live; do not expose the local monitor port.

## 12. Plan self-review

- Every launch acceptance criterion maps to P2M1T02, P2M1T03 or P2M1T04 and to an observable command/evidence type.
- The old unsafe staging behavior is explicitly blocked and assigned a bounded correction.
- Forms/Turnstile/Directus are not silently required for a static launch, but their later safety gates remain explicit.
- Credentials, Cloudflare, Nginx, Docker, public DNS, service reload and production cutover retain separate approval boundaries.
- No task authorizes a secret value, direct port exposure, irreversible deletion or unverified rollback.
- The plan remains under the 600-line project-doc limit and is ready for WBS execution only after the owner actions above are approved.
