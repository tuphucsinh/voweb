# VOweb Master Plan

**Revision:** 8
**Last reviewed:** 2026-09-03
**Status:** Production SHA `d93a44fe6ca74614d6d19f6599f9a546099f323b` is live through the Cloudflare apex/www routes; public HTTPS, VI/EN, assets, headers, TLS and loopback boundary are verified. Phase 2 static launch and the MARIGOLD visual integration are complete; admin remains deferred.
**Current candidate:** `d93a44fe6ca74614d6d19f6599f9a546099f323b`
**Confidence:** CAO

## 1. Goal and launch boundary

Publish the approved VOweb static release at `https://vorigin.vn` (and `https://www.vorigin.vn`) safely. The first launch keeps contact and partnership forms disabled (`contact_forms_enabled=false`, `launch.production_ready=true`); Turnstile, lead delivery, Directus publishing and `admin.vorigin.vn` ingress are deferred to Phase 3.

Launch must prove, independently:

- exact approved source/release identity;
- indexable production HTML and approved VI/EN content;
- loopback-only Pi services and isolated staging;
- Cloudflare HTTPS/Tunnel routing for apex and `www` without router port forwarding;
- backup, rollback and post-cutover evidence;
- no secret, private `Doc/` file or `.tmp/` artifact in the release.

`git commit`, `production_ready=true`, DNS resolution and an active `cloudflared` process are not deploy-success evidence by themselves.

## 2. Current verified state

### Repository

- Root: `/home/pi5/projects/VOweb`
- Branch: `main`; local `HEAD` and `origin/main` are `d93a44fe6ca74614d6d19f6599f9a546099f323b`.
- Candidate history contains the isolated deployment wrapper, staging Nginx config, contract tests, reconciled runbook/plan and the MARIGOLD visual integration.
- `Doc/` and `.tmp/` are pre-existing excluded paths; never stage or delete them.
- `config/site.json`: `contact_forms_enabled=false`, `launch.production_ready=true` for the production candidate.
- `ops/.env` exists with restricted permissions; values are never printed or committed.

### Application and host

- `make build`, static/copy QA, optimizer check, deployment contract tests `8/8`, preflight unit tests `3/3`, Node syntax/tests `5/5`, manifest and checksum checks passed for the candidate.
- `nginx` and `cloudflared` are active.
- `/srv/vorigin/current` points to `/srv/vorigin/releases/20260903T013840Z-production`; prior release `/srv/vorigin/releases/20260902T114252Z-production` remains available for rollback.
- Production origin remains loopback-bound at `127.0.0.1:8080`; Directus (`127.0.0.1:8055`) and lead API (`127.0.0.1:8787`) remain private loopback services.
- Isolated staging canary is deployed and verified on `127.0.0.1:8081`; only the staging Nginx site was reloaded. Production public cutover is verified separately below.

### Public edge

- **Delegation PASS:** authoritative nameservers are `peter.ns.cloudflare.com` and `shubhi.ns.cloudflare.com`.
- **Phase 2 public edge PASS:** owner-created Cloudflare Tunnel routes publish `vorigin.vn` and `www.vorigin.vn` to `http://127.0.0.1:8080`; both names resolve through the local resolver, Cloudflare DoH and Google DoH.
- **Phase 3 deferred scope (intentional):** `admin.vorigin.vn` is NXDOMAIN, which is expected deferred scope for Phase 3 and NOT a Phase 2 blocker.
- `cloudflared active` proves connector liveness only; it does not prove public-hostname ingress.

Production preflight, build/static/copy/optimizer QA, manifest/checksum integrity and deploy wrapper PASS were rerun for SHA `d93a44fe6ca74614d6d19f6599f9a546099f323b` on 2026-09-03.

## 3. Architecture and invariants

```text
public visitor (apex / www)
  -> Cloudflare HTTPS/WAF
  -> Cloudflare Tunnel
  -> Nginx 127.0.0.1:8080
  -> /srv/vorigin/current

local staging canary
  -> Nginx 127.0.0.1:8081
  -> /srv/vorigin/staging/current

Phase 3 admin (deferred)
  -> Cloudflare Access
  -> Cloudflare Tunnel
  -> Directus 127.0.0.1:8055
  -> private Docker network -> PostgreSQL
```

- No router port forwarding and no public database, Directus or lead-api listener.
- Staging uses `/srv/vorigin/staging/app`, `/srv/vorigin/staging/releases`, `/srv/vorigin/staging/current`, Nginx site `vorigin-staging` and port `8081`.
- Production uses `/srv/vorigin/app`, `/srv/vorigin/releases`, `/srv/vorigin/current`, Nginx site `vorigin` and port `8080`.
- Staging rejects `RUN_DATA_SERVICES=1`; shared data services are production-only and explicit.
- Deployment verifies manifest/checksum; it never regenerates release metadata during deploy.
- Forms remain disabled until a separate post-launch approval and real-domain test in Phase 3.
- Never read, print, commit or persist Cloudflare, Directus, Turnstile or environment secret values.

## 4. Execution sequence

### P2M1T02 — isolated canary and deployment boundary

Source boundary is committed in `b9d39f92cc16c02a1e8e095d2a1455123db6ceed`; P2M1T02 staging and boundary read-back are verified. Staging remains local-only on `/srv/vorigin/staging/current` and `127.0.0.1:8081` with `RUN_DATA_SERVICES=0`. Do not configure public DNS or Cloudflare mutations here. Evidence covers the staging root, pointer, port, Nginx site, browser routes and unchanged production pointer.

### P2M1T03 — exact production candidate

The exact production candidate and release gates were completed before public routing; the latest production PASS is bound to SHA `d93a44fe6ca74614d6d19f6599f9a546099f323b` and was independently rerun in this session.

### P2M1T04 — apex/www edge, cutover and public verification

Phase 2 public scope is strictly apex `vorigin.vn` and `www.vorigin.vn`. The owner-created Cloudflare routes and public edge are VERIFIED for production SHA `d93a44fe6ca74614d6d19f6599f9a546099f323b`.

Public evidence, `2026-09-03`: DNS resolved from the local resolver, Cloudflare DoH and Google DoH; apex `/` returned `302`, `/vi/` and `/en/` returned `200`; `www.vorigin.vn` returned `301 Location: https://vorigin.vn/`; TLS certificate validation passed with SAN match using TLS 1.3; 31/31 referenced static assets loaded; all five checked security headers were present; exact public listing/detail routes returned `200` with `Brand1.png`; `127.0.0.1:8080` remained loopback-only. No `admin.vorigin.vn` route was created.

### P3T05 — MARIGOLD featured visual integration

The approved homepage visual system was reused for the homepage, Brands listing and MARIGOLD detail surfaces. Source changes are in `build.py` and `public/styles.css`; generated output and `Brand1.png`/`Hero1.png` assets are in `dist/` and `public/assets/`. The contract is desktop `48/52`, tablet `46/54`, exact `1672/941` artwork geometry, alpha-mask transition, and text-first mobile stacking with the horizontal mask disabled.

Technical/browser verification passed before release: production build/preflight/QA, asset chain, public edge checks, exact VI/EN listing/detail routes and browser smoke with zero console errors. Commit/push/deploy was owner-authorized; release is `d93a44fe6ca74614d6d19f6599f9a546099f323b` at `/srv/vorigin/releases/20260903T013840Z-production`. Forms/data services were not enabled or refreshed.

### P3M1T01 — admin route, lead and CMS

Deferred until static launch is stable. Route contract: `admin.vorigin.vn` -> Directus `127.0.0.1:8055` through Cloudflare Tunnel + Cloudflare Access, with least-privilege roles/tokens and secret-safe verification. Configure Turnstile, enable forms, and enable CMS content sync only with separate evidence and approval.

## 5. Acceptance and evidence contract

Report these states separately; never collapse them into one readiness flag:

```text
application_state: PASS | FAIL | BLOCKED + build/content evidence
host_state:        PASS | FAIL | BLOCKED + Nginx/listener evidence
runtime_state:     PASS | FAIL | BLOCKED + process/container/health evidence
edge_state:        PASS | FAIL | BLOCKED + DNS/HTTPS/redirect evidence
rollback_state:    PASS | FAIL | BLOCKED + backup/previous-release evidence
residual_blocker:  exact owner/action or NONE
```

Required evidence by stage:

- source: `git status --short --branch`, exact SHA, `git diff --check`, scope/secret scan;
- application: build, static/copy/optimizer QA, production preflight, manifest/checksum and Node/Python tests;
- staging: `sudo nginx -t`, effective config, port `8081`, `/healthz`, browser matrix and production-pointer read-back;
- edge: at least two public recursive DNS resolvers plus local resolver, exact HTTPS routes for `vorigin.vn` and `www.vorigin.vn`, canonical redirect, security headers, denied paths and no `:8080` exposure;
- rollback: verified backup listing, previous release, approved restore command and post-restore read-back.

Lighthouse/Web Vitals is `Monitor` after public launch. Numeric overflow remains `UNKNOWN/BLOCKED_BROWSER_LAYOUT` until the CDP probe is fixed; screenshots are not numeric proof.

## 6. Approval and stop gates

Explicit approval is required for:

- writes under `/srv/vorigin`, Nginx reload or deployment-wrapper execution;
- Cloudflare DNS, Tunnel or public-hostname changes;
- changing `production_ready`, public content/legal release and creating the exact launch commit;
- production deploy, backup, rollback or public cutover.

Stop and preserve the first useful evidence if:

- DNS delegation, records or ingress point somewhere unexpected;
- staging and production share a root, pointer, port or Nginx site;
- preflight fails, exact SHA/checksum does not match or preview `noindex` remains in production;
- a non-loopback listener, unexplained restart/log regression or missing backup appears;
- a secret/private artifact is exposed;
- the same failure repeats twice without new operational evidence.

## 7. Owner actions

1. Approve the static-first launch with forms disabled.
2. Confirm the current Privacy/Terms text is approved for public use, or provide final text.
3. Retain the verified isolated staging run and its Nginx/filesystem rollback path.
4. [DONE] Cloudflare public routes for Phase 2 were created by the owner:
   - `vorigin.vn` -> `http://127.0.0.1:8080`;
   - `www.vorigin.vn` -> `http://127.0.0.1:8080`.
5. [DONE] Public cutover evidence passed for exact SHA `d93a44fe6ca74614d6d19f6599f9a546099f323b`; no admin route was created.
6. (Phase 3 deferred) Approve Cloudflare Tunnel + Access route for `admin.vorigin.vn` -> `http://127.0.0.1:8055`, Turnstile keys and form enablement.

## 8. History and source of truth

- Phase 1 is complete for the current candidate; detailed evidence is in `.ai/PHASE1_EXIT_REVIEW.md` and Git history.
- Decision rationale is in `.ai/DECISIONS_LOG.md` (`D016`).
- Operational instructions are in `DEPLOY_PI5.md`, `OPERATIONS.md` and `ops/cloudflare/README.md`.
- Active executable work is only in `tasks.md`; completed task specifications do not remain there.
