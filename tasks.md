# VOweb Execution Tasks

**Plan:** `.ai/MASTER_PLAN.md` revision 1
**State:** Phase 1 ready for sequential execution; Phase 2 blocked on owner approval.
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

## Phase 2: Owner and production closure

## Milestone M1: Approval-gated launch

### [#P2M1T01] [config/site.json, legal content, approved assets] `close_owner_content_gates()`

**Goal:** Replace owner-controlled placeholders with verified business facts, final legal text and explicit asset approval.

**Depends on:** Phase 1 exit gate

**Parallel-safe:** `no`

**Context hiện có:**
- Phone and VI address were supplied by the owner and are now present in config; the EN rendering is a working translation.
- Legal pages contain self-authored bilingual drafts and explicitly state draft status; owner approval for the review flags and official MARIGOLD asset confirmation is now recorded in config.

**Concrete changes:**
1. Receive exact owner-approved phone/address and final legal text.
2. Record asset authorization and update only corresponding launch flags.
3. Rebuild and verify bilingual public pages and claims provenance.

**Constraints:**
- `Need approval`: no runner may invent facts, legal wording or authorization.
- No production flag until all evidence is read back.

**Definition of Done:**
- Owner-approved source evidence is recorded; VI/EN pages match it.
- Preflight no longer reports these named content/legal/asset gates.
- Static/copy/browser QA pass; no production deployment occurs.
- No edit to `tasks.md`, no commit by runner.

**Status:** `[x]`

---

### [#P2M1T02] [ops/.env, Cloudflare, Directus] `configure_staging_secrets_and_roles()`

**Goal:** Configure staging-only Cloudflare/Turnstile/Access and least-privilege Directus credentials without exposing secrets.

**Depends on:** `[#P2M1T01]`

**Parallel-safe:** `no`

**Context hiện có:**
- `.env` is ignored; Compose binds Directus and lead API to loopback.
- Directus documentation requires separate create-only lead and read-only content tokens.

**Concrete changes:**
1. Populate secure staging secret store from approved values.
2. Configure Tunnel/Turnstile/Access and least-privilege Directus roles/tokens.
3. Verify only presence/scope/fingerprint, never print secret values.

**Constraints:**
- `Need approval`: credentials, permissions and external configuration.
- No production DNS/cutover; no secret committed or included in runner prompts.

**Definition of Done:**
- Staging services resolve through approved routes; loopback ports remain non-public.
- Turnstile and Directus role scopes are read back and verified.
- Secret scan is clean; rollback instructions are recorded.
- No edit to `tasks.md`, no commit by runner.

**Status:** `[BLOCKED — no approved staging credentials/runtime change]`

---

### [#P2M1T03] [staging runtime] `deploy_and_verify_staging()`

**Goal:** Deploy an atomic staging release and verify real HTTP, browser, performance, lead delivery, backup and rollback behavior.

**Depends on:** `[#P2M1T02]`

**Parallel-safe:** `no`

**Context hiện có:**
- `scripts/deploy-pi5.sh staging` builds services, writes `/srv/vorigin`, updates Nginx and reloads it.
- This is a system/runtime change and is not authorized by plan approval alone.

**Concrete changes:**
1. Capture backup/current release pointer and approved rollback target.
2. Deploy staging through the existing atomic release path.
3. Run real-domain browser matrix, measured Lighthouse/Web Vitals, Turnstile lead E2E with approved fixture, Directus/local-log verification and cleanup.
4. Exercise rollback/read-back if any gate fails.

**Constraints:**
- `Need approval`: service build/reload, staging external route and test submission.
- Never use real private customer data.
- Preserve first failure; maximum one retry with new evidence.

**Definition of Done:**
- Health, browser, QA, performance, lead delivery, backup and rollback evidence are all PASS or explicitly owner-excepted.
- Release ID/path and rollback target are recorded.
- No production DNS or production flag change.
- No edit to `tasks.md`, no commit by runner.

**Status:** `[BLOCKED — staging deploy/reload and external E2E require approval]`

---

### [#P2M1T04] [production runtime] `approve_and_cut_over_production()`

**Goal:** Perform the final production build/cutover only after every code, content, security, staging and rollback gate is verified.

**Depends on:** `[#P2M1T03]`

**Parallel-safe:** `no`

**Context hiện có:**
- Production preflight currently fails four runtime gates.
- Deployment touches Docker, Nginx, `/srv/vorigin/current` and public Cloudflare routing.

**Concrete changes:**
1. Obtain explicit owner production approval tied to the exact commit/release evidence.
2. Set `launch.production_ready=true` only after all prerequisites pass.
3. Run production preflight/build/QA, atomic deploy and post-deploy read-back.
4. Monitor health/lead path and roll back on any critical regression.

**Constraints:**
- `Need approval`: production, public DNS/external impact and service changes.
- No approval inference from Phase 1/2 technical PASS.
- No destructive cleanup of old releases until retention policy allows it.

**Definition of Done:**
- `scripts/preflight.py --production`, production build, static/copy/browser/security checks and health probes pass.
- Exact live release matches approved commit/checksums and rollback is proven.
- Owner receives evidence, residual risks and monitoring action.
- No edit to `tasks.md`, no commit by runner.

**Status:** `[BLOCKED — production approval and all prerequisites missing]`

---

## Execution reconciliation

### T13 — Phase 1 exit-gate review

**Status:** `[x]` — `.ai/PHASE1_EXIT_REVIEW.md` records VERIFIED, PARTIAL/UNKNOWN and owner-controlled blockers without converting them to PASS.

### T16 — Final verification and handoff

**Status:** `[x]` — final candidate verification is recorded in `.ai/PHASE1_EXIT_REVIEW.md`; no commit, deploy, reload or cutover was performed.
