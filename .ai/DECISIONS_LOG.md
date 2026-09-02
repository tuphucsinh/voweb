# VOweb Decisions Log

## D001 — Incremental hardening, not redesign

**Status:** Accepted
**Reason:** Current Homepage and MARIGOLD renders already establish a strong premium system. The largest gaps are bounded asset, mobile-flow, delivery and release-integrity defects.
**Consequence:** Preserve current composition, palette, typography and light→dark journey; change only evidence-backed defects.

## D002 — Existing dirty tree is protected baseline

**Status:** Accepted
**Baseline HEAD:** `ea21c1b5b6374621492db8c91018e0fab48e3ac6`
**Pre-plan diff hash:** `cd29a4fb0185317e7e5a37721a26b9fbb4c47d3578e7ad65a5ba8f4b3d2cf04c`
**Consequence:** No reset, checkout, bulk restore or cleanup of pre-existing changes. Every implementation task freezes allowed paths and reconciles runner residue independently.

## D003 — Canonical B2B asset remains immutable source

**Status:** Accepted for implementation candidate
**Canonical SHA-256:** `5aabfff04d20b85499e4d6ea22eeba2b4b6924293e72134896677a3e93cc48f5`
**Source candidate:** current `public/assets/b2b-vorigin-partner.png` / `dist/assets/b2b-vorigin-partner.png` pair.
**Consequence:** Preserve the exact original under `source-assets/`; derive WebP variants deterministically. Do not redraw the logo, invent copy or replace the image with an unmatched asset.

## D004 — Hero copy belongs in HTML

**Status:** Accepted
**Reason:** `b2b-vorigin-premium.webp` embeds English copy and icons; `build.py` overlays route copy again, and CSS crops the baked content.
**Consequence:** Production hero photography must not contain copy already rendered by HTML. Locale, accessibility and responsive crop remain controllable.

## D005 — Pillow is the only image dependency for this phase

**Status:** Accepted
**Evidence:** Pillow 11.1.0 is installed; `cwebp`, `avifenc`, ImageMagick and pngquant are absent.
**Consequence:** Add a deterministic Pillow-based optimizer with `--write` and `--check`; do not install packages merely to obtain PASS.

## D006 — Generated `dist/` is not edited manually

**Status:** Accepted
**Reason:** `build.py` copies `public/` and emits all route HTML.
**Consequence:** Source changes land in `build.py`, `public/`, `content/`, `scripts/`, `services/` or `ops/`; Mika rebuilds and verifies `dist/` before commit.

## D007 — No immutable caching for unversioned filenames

**Status:** Accepted
**Reason:** Current Nginx applies 30-day `immutable` caching to stable names such as `styles.css` and `app.js`, allowing stale clients after deployment.
**Consequence:** Use bounded cache durations plus revalidation for stable names. A full fingerprint pipeline is deferred unless measured need justifies it.

## D008 — Claims registry is the sole product-claim authority

**Status:** Accepted
**Authority:** `CONTENT_GOVERNANCE.md` and `content/claims.json`.
**Consequence:** Remove or reject stale unused per-product `vn_claims_approved` flags so future maintainers do not infer a second publication gate. Public wording may not expand in this phase.

## D009 — Local durable lead storage remains primary safety net

**Status:** Accepted
**Reason:** `persistLead()` appends to NDJSON before optional Directus/webhook delivery.
**Consequence:** Non-2xx optional delivery must be logged/tested, but local success remains independent. No schema/database migration is introduced.

## D010 — Production is a separate approval-gated phase

**Status:** Accepted
**Reason:** Production preflight currently fails seven owner/runtime gates and deployment changes services, Nginx, Docker and public edge configuration.
**Consequence:** Phase 1 may prepare and verify code only. Credentials, staging services, external test submissions, DNS and production cutover require explicit approval.

## D011 — Browser numeric layout evidence remains capability-blocked

**Status:** Accepted
**Evidence:** The browser matrix rendered 24/24 route/viewport snapshots and passed source/order/image checks, but the available CDP layout probe timed out repeatedly.
**Consequence:** Numeric overflow is reported as `BLOCKED_BROWSER_LAYOUT`; screenshots are not treated as numeric no-overflow proof.

## D012 — Lead API local durability precedes optional delivery

**Status:** Accepted
**Reason:** Directus/webhook delivery is optional and can fail independently of local storage.
**Consequence:** Local NDJSON append remains the recovery path; optional sink non-2xx responses are bounded and observable, with no schema migration.

## D013 — Owner approved legal review flags and MARIGOLD asset confirmation

**Status:** Accepted
**Evidence:** Owner instruction received: “Review legacy: duyệt” and “Marigold asset confirm duyệt”; interpreted as approval of the Privacy/Terms review flags and official MARIGOLD asset confirmation.
**Consequence:** `privacy_reviewed`, `terms_reviewed` and `official_marigold_assets_confirmed` are set to `true`; `production_ready` remains `false` until runtime prerequisites pass.

## D014 — Public contact forms disabled until later

**Status:** Accepted for current release candidate
**Reason:** Owner explicitly requested that Contact/Partnership forms temporarily stop receiving online enquiries and that Turnstile be deferred.
**Consequence:** `contact_forms_enabled=false`; generated public pages render bilingual unavailable notices, omit the active lead form and Turnstile script, and preflight skips Turnstile requirements while this flag is false. The lead API remains dormant and reversible; `production_ready` remains false.

## D015 — Local IP hash salt generated outside Git

**Status:** Accepted
**Evidence:** `IP_HASH_SALT` was generated with `openssl rand -hex 32`, stored in `ops/.env`, and the file was set to mode `600`; only format/length/permission were reported.
**Consequence:** The value is never printed, committed, included in manifests or copied into reports.
