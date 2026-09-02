# VOweb Master Plan

**Revision:** 2
**Status:** Phase 1 candidate implemented; exit review PARTIAL; Phase 2 blocked on owner/runtime gates
**Baseline HEAD:** `ea21c1b5b6374621492db8c91018e0fab48e3ac6`
**Pre-existing diff hash:** `cd29a4fb0185317e7e5a37721a26b9fbb4c47d3578e7ad65a5ba8f4b3d2cf04c`

## 1. Goal

Bring VOweb from a strong but uneven premium preview to a verified, maintainable and production-gated release without redesigning the visual system.

Observable outcome:

- Homepage, MARIGOLD, Partners and Contact are consistently premium at 390, 768 and 1440 px.
- No text is baked into hero photography where HTML already supplies that copy.
- Mobile users see product or form value without avoidable multi-screen whitespace.
- Large images have responsive delivery; content images reserve layout space.
- Unversioned assets are not cached as immutable.
- Release manifests/checksums are deterministic and verifiable.
- Static QA, browser QA and lead API tests cover the defects found in the audit.
- Production remains blocked until owner facts, legal approval, credentials and staging evidence are complete.

## 2. Verified starting state

- Static bilingual VI/EN generator: `build.py` → `dist/`.
- `python3 scripts/qa_static.py`: PASS, 32 HTML pages.
- `python3 scripts/copy_qa.py`: PASS, 28 VI/EN pages.
- Chrome 151 rendered current `dist/` at 390×844, 768×1024 and 1440×900 with no serious render log errors.
- Core visual direction is strong; Homepage and MARIGOLD are approximately 8.3–8.7/10.
- Partners hero is materially degraded by `b2b-vorigin-premium.webp`, which contains embedded copy and is cropped under HTML copy.
- MARIGOLD mobile delays the product visual; Contact mobile delays the form.
- `dist/` is 2,255,959 bytes; `b2b-vorigin-partner.png` is 1,155,665 bytes.
- Across generated HTML: 246 `<img>` tags, 48 missing width/height, zero `srcset`.
- Nginx sets 30-day `immutable` caching on unversioned asset names.
- `CHECKSUMS.sha256` fails for three entries; the `.gitignore` mismatch is a stale manifest defect because worktree equals HEAD.
- Lead API syntax passes, but optional Directus/webhook delivery does not reject HTTP error status.
- Production preflight currently fails seven owner/runtime gates; phone and address were supplied in the current owner instruction, while legal review, MARIGOLD asset authorization, Turnstile credentials, IP hash salt and the production flag remain unresolved.
- No existing `tasks.md`, `.ai/MASTER_PLAN.md` or `.ai/DECISIONS_LOG.md` existed before this revision.

## 3. Design contract

**Surface:** bilingual corporate brand/catalogue website for Vietnamese consumers and international B2B partners.
**Design read:** restrained editorial premium; credible provenance and market-entry capability; product warmth without luxury theatre.
**Authority:** `design-taste-frontend` for aesthetics; `browser-screenshot-verification` for rendered evidence.
**Implementation:** existing Python static generator, HTML/CSS/vanilla JS; no framework migration.
**Three dials:** variance 7/10, motion 4/10, density 3/10.
**Composition:** preserve current light editorial journey and light→dark B2B transition.
**Asset rule:** supplied/canonical assets remain source-of-truth; derive compressed variants without inventing logos, claims or product imagery. Copy must remain HTML, not baked into hero images.
**Responsive evidence:** 390×844, 768×1024, 1440×900; VI and EN; real Chrome stable.
**Accessibility posture:** visible focus, reduced motion, readable supporting text, reserved image geometry, semantic labels.

## 4. Scope

### In scope

- B2B hero asset cleanup and responsive integration.
- MARIGOLD mobile fold and Contact mobile conversion order.
- Small-text accessibility hardening without changing the visual identity.
- Deterministic image optimization using installed Pillow; no new dependency.
- Image dimensions, responsive variants and `srcset`/`sizes` for high-impact assets.
- Safe cache policy for unversioned files.
- Deterministic manifest/checksum generation and verification.
- Browser QA harness for critical routes/viewports.
- Lead API optional-delivery status handling, bounded rate-bucket cleanup and built-in Node tests.
- Stronger production preflight and removal of stale dual-authority claim flags.
- Approval-gated staging and production closure.

### Out of scope

- Full redesign, framework migration, CMS redesign or AI feature expansion.
- New brands, invented claims, synthetic testimonials or new product data.
- Production credentials, public DNS, deploy, service restart, database migration or external form submission without explicit approval.
- Replacing official logo/MARIGOLD assets without owner authorization.
- Manual edits to generated `dist/` as source-of-truth.

## 5. Global constraints

1. Preserve all pre-existing dirty changes; never reset the repo or overwrite concurrent user edits.
2. Before each task, Mika records current `HEAD`, status path set and allowed write paths.
3. Source changes occur in `build.py`, `public/`, `scripts/`, `services/` or `ops/`; `dist/` is regenerated only by `build.py`.
4. Runner does not edit `tasks.md`, commit, push, deploy or access secrets.
5. One task = one Mika-verified commit.
6. UI task acceptance requires Chrome screenshots, not source plausibility.
7. Production and credential tasks remain `Need approval` until the owner gate is explicit.
8. Existing claims remain governed by `content/claims.json`; no task may broaden public wording.

## 6. Phase 1 — Premium hardening and release integrity

### Milestone M1 — Visible premium blockers

Tasks: `P1M1T01`–`P1M1T05`.

Deliverables:

- Preserve canonical B2B PNG hash `5aabfff04d20b85499e4d6ea22eeba2b4b6924293e72134896677a3e93cc48f5` under `source-assets/`.
- Deterministically derive 640w and 1020w WebP variants with Pillow.
- Partners/Home use clean imagery with HTML copy; no embedded duplicate copy.
- MARIGOLD product visual appears in the first mobile experience without a dead gap.
- Contact mobile prioritizes the form ahead of the supporting card.
- Essential labels/footer/trust copy remain readable without losing the restrained visual language.

Milestone acceptance:

- VI/EN critical routes pass static/copy QA.
- 390, 768 and 1440 screenshots have no overflow, clipped text or broken asset.
- Partners hero has no duplicated/cropped embedded copy.
- At 390×844, MARIGOLD shows product imagery within the initial viewport or immediately at its lower boundary.
- At 390 px, Contact exposes the first form field before the supporting card.

Rollback: revert only the milestone commits; rebuild `dist/`; verify original source asset hash remains intact.

### Milestone M2 — Delivery, layout stability and release integrity

Tasks: `P1M2T01`–`P1M2T04`.

Deliverables:

- Generated content images have intrinsic width/height.
- High-impact hero, lineup, B2B and product imagery have responsive WebP variants and correct `srcset`/`sizes`.
- No LCP image is lazy-loaded; below-fold imagery remains lazy where appropriate.
- Unversioned assets no longer receive unsafe immutable caching.
- `MANIFEST.txt` and `CHECKSUMS.sha256` are generated deterministically and pass verification.

Milestone acceptance:

- `qa_static.py` fails on missing local dimensions and malformed responsive-image contracts.
- Generated HTML contains expected `srcset`/`sizes` on high-impact imagery.
- All production manifest entries exist; no unexpected deployable file is silently omitted.
- `sha256sum -c CHECKSUMS.sha256` returns exit 0 after generation.
- Full static/copy QA and browser matrix remain green.

Rollback: restore previous cache config and generated artifacts from task commits; no service reload in Phase 1.

### Milestone M3 — Automated quality and lead reliability

Tasks: `P1M3T01`–`P1M3T03`.

Deliverables:

- Project-local browser smoke harness covers Homepage, MARIGOLD, Partners and Contact in VI/EN at 390/768/1440.
- Assertions cover status, expected text, missing images, horizontal overflow, mobile menu accessibility and critical ordering.
- Lead API has built-in Node tests and treats Directus/webhook non-2xx responses as explicit delivery failure telemetry while preserving local append-only storage.
- Rate-limit buckets are bounded/expired.
- Production preflight requires a non-placeholder IP hash salt and enforces the single claim authority.

Milestone acceptance:

- `node --test services/lead-api/*.test.mjs` exits 0.
- Browser smoke matrix exits 0 using `/usr/bin/google-chrome-stable`.
- Preview preflight remains PASS with named warnings; production preflight remains FAIL until owner gates are complete.
- No secret value is printed or committed.

Phase 1 exit gate:

- `python3 build.py`
- `python3 scripts/qa_static.py`
- `python3 scripts/copy_qa.py`
- `python3 scripts/preflight.py`
- `node --check services/lead-api/server.mjs`
- `node --test services/lead-api/*.test.mjs`
- project browser matrix at 390/768/1440
- `sha256sum -c CHECKSUMS.sha256`
- `git diff --check`
- Mika adversarial audit: three most serious remaining issues versus requirements

Expected route: STANDARD for visual/static tasks; CONTROLLED for lead/security or production-related tasks.

## 7. Phase 2 — Owner and production closure

### Milestone M1 — Owner-controlled launch gates

Tasks: `P2M1T01`–`P2M1T04`.

This phase is not authorized for execution by plan approval alone.

Required owner inputs/approvals:

- official business phone;
- official VI/EN business address;
- final Privacy Policy and Terms of Use;
- MARIGOLD production asset authorization;
- Cloudflare Tunnel, Turnstile and Access credentials/configuration;
- Directus production roles/tokens;
- staging acceptance;
- explicit production cutover approval.

Phase acceptance:

- `scripts/preflight.py --production` PASS.
- Staging browser matrix and measured Lighthouse/Web Vitals evidence satisfy the approved thresholds or has an explicit exception.
- Real-domain Turnstile/lead delivery is verified with owner-approved test data and cleanup.
- Backup and rollback paths are read back and tested before production cutover.
- Production deploy, DNS or service changes occur only under explicit approval.

## 8. Verification matrix

- **Visual premium:** Chrome screenshots at 390/768/1440; VI/EN; Home/MARIGOLD/Partners/Contact.
- **Responsive:** no horizontal overflow; menu usable; long VI/EN text not clipped; form/product priority verified.
- **Accessibility observations:** focus visibility, semantic controls, reduced motion, readable supporting copy.
- **Static correctness:** metadata, H1, canonical, hreflang, local links/assets, claims guard, image geometry.
- **Performance evidence:** asset byte budgets and responsive contracts in Phase 1; Lighthouse only when an approved reachable HTTP target exists.
- **API:** built-in Node tests, malformed/oversize input, host/content-type/rate limit, Turnstile stub, local persistence, optional sink non-2xx.
- **Release:** deterministic MANIFEST/CHECKSUMS, source/dist parity and clean scoped diff.
- **Production:** preflight, Nginx syntax, staging health, real browser, lead E2E, backup/rollback, explicit approval.

## 9. Risks and stop conditions

Stop and report when:

- working-tree path set changes outside the current task;
- canonical asset hash differs unexpectedly;
- Pillow output is visibly degraded or non-deterministic;
- the same browser/test failure repeats twice without new evidence;
- a task requires credentials, production access, public messaging, service restart or destructive cleanup without approval;
- a generated `dist/` diff cannot be explained by source changes;
- independent review is non-PASS for lead/security/production scope.

## 10. Optimality check

A full redesign would add risk without addressing the actual blockers. The selected route preserves the strongest current work and fixes the small number of high-impact defects first. Content-hashed asset infrastructure was also rejected for this phase as unnecessary complexity; safe cache headers plus deterministic release manifests solve the current failure mode with lower maintenance cost.
