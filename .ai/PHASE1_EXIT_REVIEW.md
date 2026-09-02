# Phase 1 Exit-Gate Review

**Date:** 2026-08-31
**Verdict:** `PARTIAL — technical candidate verified; owner/runtime gates remain blocked`

## VERIFIED

- T01–T07: premium/responsive implementation evidence retained in `/home/pi5/hermes-artifacts/browser-evidence/VOweb/`.
- T08: Nginx candidate removes `immutable` from stable CSS/JS; `nginx -t` is `BLOCKED_ENVIRONMENT` because Nginx is not installed on this host. No reload occurred.
- T09: deterministic release manifest/checksum; `MANIFEST.txt` 243 files, `CHECKSUMS.sha256` 241 entries, `sha256sum -c` 241/241 OK.
- T11: `node --test tests/lead-api.test.mjs` 5/5; CLI `/healthz` loopback returned HTTP 200; listener was stopped after smoke.
- T12: preview preflight PASS with 3 expected warnings; production preflight fails closed with 7 named blockers; active legacy product claim flag search PASS.
- Build/static/copy/image gates: build 32 pages, static QA PASS, copy QA 28 VI/EN PASS, optimizer check PASS, Python compile PASS, `git diff --check` PASS.
- Contact facts supplied by owner are present in `config/site.json`: phone and VI/EN address.
- Terms and Privacy pages now contain bilingual self-authored draft policy text and an explicit draft/review notice.
- Owner approval received for the Privacy/Terms review flags and official MARIGOLD asset confirmation; corresponding config flags are true.
- `IP_HASH_SALT` is present in local `ops/.env` with mode `600`; its value is intentionally excluded from evidence.
- Public contact/partnership forms are now disabled by explicit config; rendered VI/EN Contact pages show the temporary-unavailable notice, contain no active lead form and load no Turnstile script.

## PARTIAL / UNKNOWN

- T10 browser matrix: 24/24 route/viewport snapshots and static/browser asset/order checks PASS at 390×844, 768×1024 and 1440×900. Numeric `scrollWidth`/bounding-box overflow proof is `BLOCKED_BROWSER_LAYOUT` because the available CDP runtime repeatedly timed out. This is not a numeric no-overflow PASS.
- Lighthouse/Web Vitals and automated accessibility conformance: `UNKNOWN`; no approved measurement tool was available and none was installed.
- Nginx effective response test: `BLOCKED_ENVIRONMENT`; config inspection passed, live header behavior was not exercised.
- Static security scanner found no XSS/eval sinks or dependency markers, but flags the existing inline `--flavor` style and external font URLs for separate CSP/header review.

## OWNER / PRODUCTION BLOCKERS REMAINING

1. `launch.production_ready=false`.

Turnstile keys are intentionally deferred and are not blockers while `contact_forms_enabled=false`. `IP_HASH_SALT` is present in local `ops/.env`; production preflight was run with that env loaded and returned exactly this one blocker.

No production DNS, deploy, reload, external form submission, credential change, or cutover was performed.
