# VOweb Execution Tasks

**Plan:** `.ai/MASTER_PLAN.md` revision 3
**State:** Phase 1 candidate pushed; Phase 2 is deployment-first and blocked on public edge, isolated canary and explicit cutover approval.
**Global rule:** Runner edits only task-declared source paths, never `tasks.md`, never commits, never deploys. Mika rebuilds `dist/`, verifies, ticks and commits one task at a time.

## Phase 1: Premium hardening and release integrity

## Milestone M1: Visible premium blockers

### [#P1M1T01] [scripts/optimize_images.py, source-assets/, public/assets/] `optimize_image(source, variants, mode): Report`

**Goal:** Preserve the clean B2B image as canonical source and derive deterministic, browser-ready variants without adding dependencies.

**Depends on:** `none`

**Parallel-safe:** `no`

**New interface:**
```python
optimize_image(source: Path, variants: list[Variant], mode: Literal["write", "check"]) -> Report
# CLI: python3 scripts/optimize_images.py --write
# CLI: python3 scripts/optimize_images.py --check
```

**Context hiện có:**
- Canonical candidate exists at `public/assets/b2b-vorigin-partner.png` and `dist/assets/b2b-vorigin-partner.png`; SHA-256 must remain `5aabfff04d20b85499e4d6ea22eeba2b4b6924293e72134896677a3e93cc48f5`.
- Pillow 11.1.0 is available; no `cwebp`, `avifenc` or ImageMagick.

**Concrete changes:**
1. Preserve the exact PNG at `source-assets/b2b-vorigin-partner.png`.
2. Add deterministic Pillow conversion for 640w and 1020w WebP variants, preserving aspect ratio and sRGB output.
3. Write only declared outputs under `public/assets/`; `--check` regenerates in memory and fails on byte/hash drift.
4. Remove the unoptimized public PNG only after canonical hash and generated variants are verified; `dist/` removal happens through rebuild.

**Constraints:**
- No upscaling, logo redraw, AI regeneration, crop or copy baked into the image.
- Desktop WebP target ≤250KB; mobile WebP target ≤120KB unless visual review proves the budget unsafe.
- No new package installation.

**Definition of Done:**
- Mika runs `python3 scripts/optimize_images.py --write && python3 scripts/optimize_images.py --check` with exit 0.
- Canonical PNG hash matches D003; generated files decode and have declared dimensions.
- Visual inspection shows no banding, logo damage or composition change.
- No edit to `tasks.md`, no commit by runner.

**Status:** `[x]`

---

### [#P1M1T02] [build.py, public/styles.css] `render_b2b_picture(locale): str`

**Goal:** Replace the broken text-baked Partners hero and heavy Homepage B2B image with clean responsive imagery while retaining copy as localized HTML.

**Depends on:** `[#P1M1T01]`

**Parallel-safe:** `no`

**New interface:**
```python
render_b2b_picture(css_class: str, alt_text: str, loading: str = "lazy") -> str
# Emits <picture> with 640w/1020w WebP srcset and intrinsic dimensions.
```

**Context hiện có:**
- `build.py` Homepage market block uses `b2b-vorigin-partner.png`; Partners hero uses `b2b-vorigin-premium.webp` with embedded English copy.
- `public/styles.css` applies `object-fit: cover` to `.partner-hero-visual img` and uses the PNG in `.sunset-bleed`.

**Concrete changes:**
1. Add one helper for the B2B `<picture>` contract and use it on Homepage and Partners.
2. Point `.sunset-bleed` to the optimized desktop WebP.
3. Calibrate `object-position` separately for Homepage and Partners without crop-sensitive baked copy.
4. Keep VI/EN headline, paragraph, icons and CTA in HTML only.

**Constraints:**
- Preserve current dark cinematic section and light→dark transition.
- Do not change claims, CTA destinations or language copy.
- Do not reference `b2b-vorigin-premium.webp` from generated public pages after this task.

**Definition of Done:**
- `python3 build.py && python3 scripts/qa_static.py && python3 scripts/copy_qa.py` exit 0.
- Search of `dist/**/*.html` finds zero references to `b2b-vorigin-premium.webp`.
- Chrome screenshots for VI/EN Partners and Homepage at 390/768/1440 show no duplicated/cropped image text and no horizontal overflow.
- No edit to `tasks.md`, no commit by runner.

**Status:** `[x]`

---

### [#P1M1T03] [public/styles.css] `MARIGOLD mobile hero fold`

**Goal:** Remove the excessive mobile dead space so the MARIGOLD product lineup appears within the initial 390×844 experience or at its lower boundary.

**Depends on:** `[#P1M1T02]`

**Parallel-safe:** `no`

**Context hiện có:**
- `.marigold-hero-grid` has a desktop minimum height; mobile rules set padding and `.marigold-hero-visual` minimum height but still delay the lineup.
- Trust chips and source link must remain visible and readable.

**Concrete changes:**
1. Adjust only mobile grid spacing/min-height/order required to bring the product visual forward.
2. Preserve trust chips, source link and product aspect ratio.
3. Check both Vietnamese and English wrapping at 390 and 430 px.

**Constraints:**
- No desktop/tablet composition change.
- No absolute positioning that overlaps copy or bypasses natural document flow.
- Product image may not be cropped or upscaled beyond its existing presentation contract.

**Definition of Done:**
- Chrome 390×844 screenshots for VI/EN MARIGOLD show product imagery within the initial viewport or touching its lower boundary.
- 768×1024 and 1440×900 screenshots remain visually equivalent except intentional responsive behavior.
- Static/copy QA pass and no horizontal overflow is measured.
- No edit to `tasks.md`, no commit by runner.

**Status:** `[x]`

---

### [#P1M1T04] [build.py, public/styles.css] `Contact mobile form priority`

**Goal:** Reduce mobile conversion friction by presenting the contact form before the supporting relationship card while preserving the desktop two-column layout.

**Depends on:** `[#P1M1T03]`

**Parallel-safe:** `no`

**Context hiện có:**
- `build.py::contact()` emits `<aside class="contact-aside">` before `<div class="form-wrap">`.
- At 390×1200, the form is still below the visible area after the hero and full aside.

**Concrete changes:**
1. Preserve semantic DOM or use explicit responsive ordering so mobile presents `.form-wrap` before `.contact-aside`.
2. Keep the desktop 34/66 layout and sticky aside.
3. Preserve disabled preview state, Turnstile note, field labels and live status region.

**Constraints:**
- No form submission or external test in this task.
- No change to `/api/lead`, validation limits or contact copy.
- Keyboard order must match visual order on mobile.

**Definition of Done:**
- At 390 px, the first form field appears before the relationship card and within the first 1000 CSS px after navigation.
- Desktop 1440×900 keeps aside left/form right; tablet/mobile have no overflow.
- VI/EN Contact static/copy QA and Chrome screenshot checks pass.
- No edit to `tasks.md`, no commit by runner.

**Status:** `[x]`

---

### [#P1M1T05] [public/styles.css] `supporting-text readability floor`

**Goal:** Improve readability of critical navigation, trust, service and footer text without losing the restrained premium hierarchy.

**Depends on:** `[#P1M1T04]`

**Parallel-safe:** `no`

**Context hiện có:**
- Multiple user-facing labels use 8–10px text, including tags, service labels, footer links and trust-chip copy.
- Decorative eyebrow hierarchy may remain small where contrast and uppercase tracking are adequate.

**Concrete changes:**
1. Raise essential interactive/supporting text to a practical floor (generally 10–12px by role).
2. Preserve typographic hierarchy, line length and existing palette.
3. Re-check footer wrapping, 5-service row/scroll, trust chips and mobile card heights.

**Constraints:**
- Do not globally inflate all typography.
- Do not reduce contrast or touch target sizes.
- No new font family or visual direction.

**Definition of Done:**
- Chrome 390/768/1440 screenshots show readable labels with no new wrap/crop regression.
- Focus indicators and 44px primary button targets remain intact.
- Static/copy QA pass; visual review records before/after evidence.
- No edit to `tasks.md`, no commit by runner.

**Status:** `[x]`

---

## Milestone M2: Delivery, layout stability and release integrity

### [#P1M2T01] [build.py, scripts/qa_static.py] `image_geometry_contract(img): ValidationResult`

**Goal:** Eliminate avoidable layout shift by giving generated content images intrinsic dimensions and enforcing the contract in QA.

**Depends on:** `[#P1M1T05]`

**Parallel-safe:** `no`

**New interface:**
```python
# qa_static.py
validate_image_geometry(attrs: dict[str, str], page: Path) -> list[str]
```

**Context hiện có:**
- Current generated HTML has 246 image tags; 48 are missing width or height.
- Existing QA checks alt text and local asset existence but not intrinsic geometry.

**Concrete changes:**
1. Add correct width/height for brand, product, editorial and partner imagery generated by `build.py`.
2. Preserve decorative icon contracts already carrying 24×24 dimensions.
3. Extend QA to fail local content images without valid positive width and height; allow only documented exceptions.
4. Verify LCP hero images are not lazy and below-fold imagery remains lazy where appropriate.

**Constraints:**
- Dimensions must match source aspect ratio; CSS remains responsible for responsive display size.
- No hardcoded false dimensions to silence QA.
- Do not require width/height for remote third-party widgets.

**Definition of Done:**
- `python3 build.py && python3 scripts/qa_static.py` exit 0.
- Audit parser reports zero undocumented local content images missing width/height.
- 390/768/1440 screenshots show no aspect distortion.
- No edit to `tasks.md`, no commit by runner.

**Status:** `[x]`

---

### [#P1M2T02] [scripts/optimize_images.py, build.py, public/assets/] `responsive_picture(asset_key, alt, policy): str`

**Goal:** Add responsive delivery for high-impact MARIGOLD hero, lineup, product and B2B imagery so mobile does not download desktop-sized assets unnecessarily.

**Depends on:** `[#P1M1T01]`, `[#P1M2T01]`

**Parallel-safe:** `no`

**New interface:**
```python
responsive_picture(asset_key: str, alt: str, policy: ImagePolicy) -> str
# ImagePolicy declares widths, sizes, loading, fetchpriority and CSS class.
```

**Context hiện có:**
- Generated HTML has zero `srcset`.
- Existing heavy sources include 1494w hero, 1300w lineup, 780w product assets and the B2B source.

**Concrete changes:**
1. Extend deterministic optimizer declarations for approved heavy sources and bounded WebP widths without upscaling.
2. Emit `<picture>`/`srcset`/`sizes` for Homepage hero, MARIGOLD lineup, product heroes/cards and B2B imagery.
3. Keep `fetchpriority="high"` only on route LCP imagery; keep below-fold variants lazy.
4. Add QA checks for declared responsive contracts and missing generated files.

**Constraints:**
- No AVIF dependency in this phase.
- Do not duplicate near-identical variants that save negligible bytes.
- Preserve source assets and image quality; browser fallback remains valid.

**Definition of Done:**
- `optimize_images.py --check`, build and static/copy QA exit 0.
- Generated critical pages contain expected `srcset` and `sizes`; all referenced files exist.
- Mobile selected-candidate evidence shows a smaller variant is eligible at 390 px.
- Browser matrix shows no quality/crop regression.
- No edit to `tasks.md`, no commit by runner.

**Status:** `[x]`

---

### [#P1M2T03] [ops/nginx/vorigin.conf] `safe cache policy for stable filenames`

**Goal:** Prevent 30-day stale CSS/JS/assets after deployment while retaining effective browser/CDN caching.

**Depends on:** `none`

**Parallel-safe:** `yes`

**Context hiện có:**
- The static asset location applies `max-age=2592000, immutable` to stable unversioned names such as `styles.css` and `app.js`.
- Cloudflare/Nginx may still revalidate using ETag/Last-Modified when policy permits.

**Concrete changes:**
1. Remove `immutable` from unversioned resources.
2. Define bounded cache/revalidation policy, separating CSS/JS from long-lived media only where maintainable.
3. Preserve gzip and all security headers at effective response scope; account for Nginx `add_header` inheritance.
4. Document the policy in `OPERATIONS.md` if operator action changes.

**Constraints:**
- No Nginx reload or system change in Phase 1.
- No content-hash pipeline in this task.
- Security headers must not disappear from asset responses because of nested `add_header` behavior.

**Definition of Done:**
- Static config inspection shows no `immutable` on unhashed names.
- `nginx -t` is run only in an approved isolated/staging environment and exits 0; otherwise record `BLOCKED_ENVIRONMENT` without false PASS.
- Config diff preserves loopback binding and security directives.
- No edit to `tasks.md`, no commit by runner.

**Status:** `[x]`

---

### [#P1M2T04] [scripts/generate_release_manifest.py, MANIFEST.txt, CHECKSUMS.sha256] `generate_manifest(root, mode): Report`

**Goal:** Make release contents and checksums deterministic so a stale manifest cannot report false integrity.

**Depends on:** `[#P1M2T02]`, `[#P1M2T03]`

**Parallel-safe:** `no`

**New interface:**
```python
generate_manifest(root: Path, mode: Literal["write", "check"]) -> Report
# CLI: python3 scripts/generate_release_manifest.py --write|--check
```

**Context hiện có:**
- Current checksum verification fails for `.gitignore`, `build.py` and `public/styles.css`.
- `MANIFEST.txt` is a hand-maintained deployable file list and omits current new B2B files.

**Concrete changes:**
1. Define deterministic inclusion/exclusion rules for production package files; exclude `.git`, secrets, caches, artifacts, backups and `Doc/` unless explicitly approved.
2. Generate sorted `MANIFEST.txt` and SHA-256 entries from the same file set.
3. Make `--check` fail on missing entries, unexpected deployable files, hash drift or secret-bearing paths.
4. Wire check mode into build/release verification scripts without mutating during check.

**Constraints:**
- Never include `ops/.env`, credentials, `.git/`, `__pycache__/` or Hermes artifacts.
- Generation must be idempotent and stable across repeated runs.
- Do not hide a mismatch by weakening verification.

**Definition of Done:**
- Two consecutive `--write` runs produce identical hashes.
- `python3 scripts/generate_release_manifest.py --check` and `sha256sum -c CHECKSUMS.sha256` exit 0.
- New responsive assets are listed; forbidden paths are absent.
- Full build/static/copy QA remains green.
- No edit to `tasks.md`, no commit by runner.

**Status:** `[x]`

---

## Milestone M3: Automated quality and lead reliability

### [#P1M3T01] [tests/browser-verify.sh, tests/browser-assert.mjs, scripts/browser_matrix.py] `run_matrix(routes, viewports): Report`

**Goal:** Turn the audited route/viewport matrix into deterministic browser smoke evidence using real Chrome stable.

**Depends on:** `[#P1M2T04]`

**Parallel-safe:** `no`

**New interface:**
```text
python3 scripts/browser_matrix.py --base-url http://127.0.0.1:8080
# Routes: VI/EN Home, MARIGOLD, Partners, Contact
# Viewports: 390x844, 768x1024, 1440x900
```

**Context hiện có:**
- No project tests exist.
- Canonical Chrome path is `/usr/bin/google-chrome-stable`.
- Standard helper source is `~/.hermes/workspaces/browser-verify.sh`.

**Concrete changes:**
1. Add project-local fixed browser helper/assertions without installing Playwright.
2. Assert HTTP success, expected locale text, zero missing local images, no horizontal overflow and accessible mobile menu state.
3. Add critical ordering assertions: clean Partners hero, MARIGOLD mobile product visibility, Contact mobile form-before-aside.
4. Save screenshots/logs only under a declared ignored artifact directory or `/home/pi5/hermes-artifacts/`.

**Constraints:**
- Fixed local/staging URLs only; no login, form submission or production navigation.
- Harness must fail closed if the server/route/browser is unavailable.
- Evidence files must not enter the release manifest.

**Definition of Done:**
- With an approved local server, matrix exits 0 and emits route/viewport evidence.
- Deliberately broken overflow/missing-image fixtures make assertions fail.
- Full static/copy QA remains green; no new dependency or lockfile.
- Matrix evidence: 24/24 route/viewport snapshots passed; numeric CDP layout probe remains `BLOCKED_BROWSER_LAYOUT` and is not treated as PASS.

**Status:** `[x]`

---

### [#P1M3T02] [services/lead-api/server.mjs, tests/lead-api.test.mjs] `createLeadServer(config, deps): http.Server`

**Goal:** Make lead handling testable and ensure optional Directus/webhook HTTP failures are observable without weakening local durable storage.

**Depends on:** `none`

**Parallel-safe:** `yes`

**New interface:**
```js
export function createLeadServer(config, deps = { fetch, fs, now, randomUUID }) { /* returns http.Server */ }
export async function postOptionalSink(url, payload, options) { /* rejects non-2xx */ }
```

**Context hiện có:**
- `persistLead()` appends NDJSON before optional sinks.
- Optional sink fetches catch exceptions but do not check response status.
- Rate-limit bucket keys are never globally expired.

**Concrete changes:**
1. Refactor server construction behind an export while preserving CLI startup behavior.
2. Reject/log optional sink non-2xx responses with bounded, non-secret messages; local lead success remains durable.
3. Add bounded bucket expiry/cleanup to prevent unbounded unique-IP growth.
4. Add built-in `node:test` coverage for host/content-type, validation, honeypot, rate limit, Turnstile outcomes, local persist, non-2xx sink and oversize behavior.

**Constraints:**
- No external HTTP call, real Turnstile, real Directus or webhook in tests.
- No secret/token/IP value in logs or fixtures.
- No database/schema change; port remains loopback-bound by Compose.

**Definition of Done:**
- `node --check services/lead-api/server.mjs` exits 0.
- `node --test tests/lead-api.test.mjs` exits 0 and exercises real request/response boundaries with injected local stubs.
- Local append occurs before optional delivery and remains recoverable when sinks fail.
- No commit by runner.

**Status:** `[x]`

---

### [#P1M3T03] [scripts/preflight.py, content/products/*.json, CONTENT_GOVERNANCE.md] `validate_production_environment(site, claims, env): list[Issue]`

**Goal:** Strengthen production fail-closed behavior and remove stale per-product claim flags that conflict with the documented single claims authority.

**Depends on:** `[#P1M3T02]`

**Parallel-safe:** `no`

**New interface:**
```python
validate_production_environment(site: dict, claims: dict, env: Mapping[str, str]) -> list[Issue]
```

**Context hiện có:**
- `content/claims.json` is the governance authority.
- Product JSON files contain unused `vn_claims_approved:false` fields.
- Lead API falls back to `IP_HASH_SALT="change-me"`; init script normally generates a real value, but production preflight does not verify it.

**Concrete changes:**
1. Remove the unused per-product claim flag and document `content/claims.json` as sole publication authority.
2. Refactor preflight checks into testable functions without changing current preview warning semantics.
3. In production mode, reject absent/placeholder `IP_HASH_SALT` in addition to existing owner/Turnstile gates.
4. Add focused Python tests or fixture-driven checks for preview warnings, production failures and public-claim invariants.

**Constraints:**
- Do not change public claim wording or mark any owner gate approved.
- Never print secret values; only report missing/placeholder field names.
- Directus/webhook remain optional unless owner policy changes.

**Definition of Done:**
- Preview preflight remains PASS with expected warnings on current config.
- Production preflight fails on current owner gates and placeholder/missing salt.
- Focused preflight tests and full static/copy QA exit 0.
- Search finds no `vn_claims_approved` outside migration/history evidence.

**Status:** `[x]`

---

## Phase 2: Deployment-first public static launch
## Milestone M1: Edge and canary boundary

### [#P2M1T01] [config/site.json, legal content, approved assets] `close_owner_content_gates()`

**Goal:** Close only the owner-controlled content and asset gates already approved, without enabling production readiness.

**Depends on:** Phase 1 exit gate

**Parallel-safe:** `no`

**Context hiện có:**
- Phone, VI/EN address, legal review flags and official MARIGOLD asset confirmation are recorded in `config/site.json`.
- `contact_forms_enabled=false` and `launch.production_ready=false` remain intentional.

**Concrete changes:**
1. Keep the verified owner facts and claim authority unchanged.
2. Preserve the forms-disabled launch boundary.
3. Do not flip `production_ready` in this task.

**Constraints:**
- No invented facts, legal text or authorization.
- No production deployment, DNS change or service reload.

**Definition of Done:**
- Owner-controlled facts are represented in VI/EN output and the current candidate remains statically verified.
- `launch.production_ready` remains `false` until the exact launch-candidate approval task.
- No edit to `tasks.md`, no commit by runner.

**Status:** `[x]`

---

### [#P2M1T02] [scripts/deploy-pi5.sh, ops/nginx/vorigin-staging.conf, tests/test_deploy_script_contract.py, DEPLOY_PI5.md] `establish_edge_and_isolated_canary()`

**Goal:** Verify the public edge, enforce deployment integrity by removing manifest self-write, make staging/canary isolated on port 8081 without mutating production `/srv/vorigin/current`, and make data-service refresh opt-in for production only while rejecting it in staging.

**Depends on:** `[#P2M1T01]`

**Parallel-safe:** `no`

**New interface:**
```text
staging deploy -> /srv/vorigin/staging/current -> 127.0.0.1:8081 (static-only; rejects RUN_DATA_SERVICES=1)
production deploy -> /srv/vorigin/current -> 127.0.0.1:8080 (RUN_DATA_SERVICES=1 opt-in with approval)
```

**Context hiện có:**
- `scripts/deploy-pi5.sh staging` previously wrote the production `current` pointer and reloaded the production Nginx origin; mode-aware paths and `ops/nginx/vorigin-staging.conf` isolate staging completely.
- `ops/docker-compose.yml` defines a single shared stack (`name: vorigin`); staging must fail closed if `RUN_DATA_SERVICES=1` is passed to prevent mutating production-shared data services.
- Nginx sources: `ops/nginx/vorigin.conf` (production port 8080), `ops/nginx/vorigin-staging.conf` (staging port 8081); public edge instructions are in `ops/cloudflare/README.md`.
- Contract tests are in `tests/test_deploy_script_contract.py`.
- Current Nginx and cloudflared services are active; `vorigin.vn` and `www.vorigin.vn` currently do not resolve from this host.

**Concrete changes:**
1. Capture current SHA/status, current release target, release list, active/effective Nginx config, listeners, Docker state and cloudflared status.
2. Remove `generate_release_manifest.py --write` from `scripts/deploy-pi5.sh` so deploy verifies `generate_release_manifest.py --check` and `sha256sum -c CHECKSUMS.sha256` without mutating workspace integrity metadata.
3. Use safe variable fallback `TURNSTILE_SITE_KEY="${TURNSTILE_SITE_KEY:-}"` in production build step.
4. Implement mode-aware deployment paths:
   - Staging: `APP_ROOT=/srv/vorigin/staging/app`, `RELEASE_ROOT=/srv/vorigin/staging/releases`, `CURRENT_LINK=/srv/vorigin/staging/current`, `NGINX_CONFIG=ops/nginx/vorigin-staging.conf`, `NGINX_SITE=vorigin-staging`, `ORIGIN_PORT=8081`.
   - Production: `APP_ROOT=/srv/vorigin/app`, `RELEASE_ROOT=/srv/vorigin/releases`, `CURRENT_LINK=/srv/vorigin/current`, `NGINX_CONFIG=ops/nginx/vorigin.conf`, `NGINX_SITE=vorigin`, `ORIGIN_PORT=8080`.
5. Add dedicated staging Nginx server block `ops/nginx/vorigin-staging.conf` for 127.0.0.1:8081 default_server serving `/srv/vorigin/staging/current` with security headers, without production hostnames or lead API proxying.
6. Gate docker compose behind `RUN_DATA_SERVICES="${RUN_DATA_SERVICES:-0}"` (validated 0/1); staging rejects `RUN_DATA_SERVICES=1` before build/runtime side effects; production uses explicit command branches for `docker compose` and `docker-compose` without unquoted variables.
7. Add stdlib contract tests in `tests/test_deploy_script_contract.py` validating manifest check-only integrity, variable expansion, staging rejection of shared data services, explicit production Compose execution branches, isolated roots/pointers/ports, Nginx staging config, and documentation contracts.
8. Update `DEPLOY_PI5.md` with staging 8081 verification, healthz endpoint, staging static-only boundary rejecting shared data services, and production-only opt-in `RUN_DATA_SERVICES=1` instructions.
9. With explicit owner approval, configure/verify Cloudflare public hostnames: apex and `www` to the Nginx origin, and `admin` behind Access only.
10. Verify public DNS, HTTPS, redirects, headers and safe denied-path behavior without reading the tunnel token.

**Constraints:**
- Credentials, Cloudflare changes, Nginx reload and `/srv/vorigin` writes require approval.
- No secret value in prompts, logs or evidence.
- If DNS or public-hostname ingress is absent, stop with `BLOCKED_EXTERNAL_ROUTE_CONFIGURATION`.
- Preserve the existing production release pointer during canary work.

**Definition of Done:**
- Deployment script uses manifest `--check` only and never writes/regenerates manifest during deploy.
- Staging/canary has distinct release root, pointer and port (8081); canary switch cannot touch `/srv/vorigin/current` or production Nginx config.
- Staging rejects `RUN_DATA_SERVICES=1` before build/runtime mutation; static deploys run without data service refresh unless `RUN_DATA_SERVICES=1` is explicitly set in production mode.
- `python3 -m unittest tests/test_deploy_script_contract.py` passes.
- `sudo nginx -t`, `sudo nginx -T`, listener and Host-header evidence pass when executed.
- `vorigin.vn` and `www.vorigin.vn` resolve and the approved route is observable, or the exact missing owner action is recorded.
- No edit to `tasks.md` by runner, no commit by runner.

**Status:** `[BLOCKED — public DNS/hostname route and isolated canary boundary require approval]`

---

## Milestone M2: Exact launch candidate

### [#P2M1T03] [config/site.json, build.py, dist/, MANIFEST.txt, CHECKSUMS.sha256] `prepare_exact_production_candidate()`

**Goal:** Produce an indexable production artifact whose exact commit, generated output, preflight and rollback identity are known before cutover.

**Depends on:** `[#P2M1T02]`

**Parallel-safe:** `no`

**Context hiện có:**
- Current candidate is `ab32d1cf8863cc6c037e114c1159a1114213b095`; its static release is currently preview/noindex and has `production_ready=false`.
- `ops/.env` exists with mode `600`; `IP_HASH_SALT` is present there but must never be printed.

**Concrete changes:**
1. Freeze the exact source/status baseline and exclude `Doc/` and `.tmp/` from release scope.
2. Obtain owner approval for the static-first launch with forms disabled and for public use of the current Privacy/Terms text; if not approved, stop.
3. Mika changes only `config/site.json` `launch.production_ready` to `true`, then rebuilds through `build.py`; no manual `dist/` edits.
4. Run production preflight through the same secret-safe environment boundary as the deploy wrapper:
   `set -a; source ops/.env; set +a; python3 scripts/preflight.py --production`.
5. Run production build, static/copy/optimizer checks, manifest/checksum checks, Python/Node checks and the browser matrix against an isolated production artifact.
6. Verify production `robots.txt` is indexable, preview `noindex` is absent, forms remain disabled and VI/EN output matches approved content.
7. Review diff, diff-check, manifest scope and secret-like paths; create the exact launch commit only after all gates pass.

**Constraints:**
- `production_ready=true` requires owner approval and exact evidence; it is not a readiness shortcut.
- Do not print or persist any value from `ops/.env`.
- Preserve the prior pushed candidate and rollback target.

**Definition of Done:**
- Production preflight returns `PASS` with `ops/.env` loaded.
- Production build/static/copy/browser/manifest/checksum gates pass and are bound to the launch SHA.
- No secret, private `Doc/` file or `.tmp/` artifact is staged.
- No production service reload or cutover occurs in this task.

**Status:** `[BLOCKED — exact launch candidate and owner public-content approval pending]`

---

## Milestone M3: Production cutover and public verification

### [#P2M1T04] [production runtime] `approve_and_cut_over_production()`

**Goal:** Atomically publish the approved launch SHA on `vorigin.vn`, verify application/host/runtime/edge separately and retain a tested rollback target.

**Depends on:** `[#P2M1T03]`

**Parallel-safe:** `no`

**Context hiện có:**
- `/srv/vorigin/current` points to `20260831T035626Z-production`, which differs from the repository candidate HTML.
- Nginx/cloudflared/Docker are active, but public DNS is currently unresolved and health/backup timers are not installed/enabled.

**Concrete changes:**
1. Obtain explicit cutover approval tied to the exact launch SHA, release path, maintenance window and rollback command.
2. Capture the immediate pre-cutover release/config/listener/container/cloudflared/disk/log baseline.
3. Run the approved backup path and verify archive listing/metadata before mutation.
4. Run the audited production deploy wrapper for the exact SHA; preserve the first useful failure and do not retry without new evidence.
5. Read back the current pointer, release files, effective Nginx config, listeners, health endpoint, container state and startup/fatal logs.
6. Verify public apex/www HTTPS routes, TLS, redirects, security headers, denied paths and no origin-port exposure.
7. Run read-only browser smoke at mobile/tablet/desktop sizes; assert the forms-disabled contract.
8. On a critical failure, stop and perform only the approved rollback, then re-verify all four boundaries and the release pointer.

**Constraints:**
- Production, public DNS, service reload, Docker state and rollback are separate approval boundaries.
- No data migration, lead submission, credential exposure or destructive old-release cleanup.
- A running container without native health evidence is reported as `running`, not `healthy`.

**Definition of Done:**
- `application_state=PASS`, `host_state=PASS`, `runtime_state=PASS`, `edge_state=PASS`, `rollback_state=PASS` with evidence paths.
- Public `vorigin.vn` serves the approved launch SHA and `www` follows the approved canonical behavior.
- Previous release and backup are read back and remain available.
- No edit to `tasks.md`, no commit by runner.

**Status:** `[BLOCKED — exact launch SHA, public DNS and explicit production cutover approval missing]`

---

## Phase 3: Post-launch lead and CMS enablement

### [#P3M1T01] [Turnstile, services/lead-api/, services/directus/] `enable_lead_and_cms_after_static_launch()`

**Goal:** Enable online enquiries and CMS publishing only after the static public launch is stable.

**Depends on:** `[#P2M1T04]`

**Parallel-safe:** `no`

**Context hiện có:**
- Public forms are intentionally disabled; Turnstile and Directus credentials are not launch prerequisites.
- Directus must remain private and use separate least-privilege lead/create and content/read scopes.

**Concrete changes:**
1. Configure approved Turnstile widget/secret through the secure runtime store.
2. Create/read back Directus roles and token scopes without exposing values.
3. Enable forms only with an owner-approved fixture, real-domain E2E, exact-ID cleanup and multidimensional baseline verification.
4. Enable content sync only after publish/rollback behavior is proven.

**Constraints:**
- No production data mutation or broad cleanup; no real customer data.
- Preserve local lead durability if optional sinks fail.

**Definition of Done:**
- Lead/CMS evidence, cleanup, rollback and monitoring are separately reviewed and pass.
- This phase cannot be used to justify bypassing the static launch gates.

**Status:** `[DEFERRED — static launch first]`

---
## Execution reconciliation

### T13 — Phase 1 exit-gate review

**Status:** `[x]` — `.ai/PHASE1_EXIT_REVIEW.md` records VERIFIED, PARTIAL/UNKNOWN and owner-controlled blockers without converting them to PASS.

### T16 — Final verification and handoff

**Status:** `[x]` — final candidate verification is recorded in `.ai/PHASE1_EXIT_REVIEW.md`; no commit, deploy, reload or cutover was performed.
