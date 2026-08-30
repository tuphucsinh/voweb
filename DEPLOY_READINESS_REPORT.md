# VOrigin Production rc7-pi5 — Deploy Readiness

## Status

- **Pi 5 staging:** READY
- **Public production:** GATED by owner-controlled configuration/content approvals listed in `CURRENT_BLOCKERS.md`
- **Public site architecture:** static build behind Nginx
- **CMS:** Directus + PostgreSQL, loopback-only on the Pi
- **Lead API:** loopback-only, intended to be reached through Nginx/Cloudflare
- **Public edge:** Cloudflare Tunnel / TLS / WAF / Turnstile

## Current build

- Bilingual VI/EN site
- Homepage, About, Brands, MARIGOLD, product pages, Capabilities, Partners, Insights, Contact, Privacy/Terms scaffolding
- Premium SVG icon system
- Latest premium MARIGOLD hero asset integrated
- Exclusive-distribution wording hidden from all public pages
- Preview build is noindex by design

## Validation required for every release

```bash
python3 build.py
python3 scripts/qa_static.py
python3 scripts/copy_qa.py
python3 scripts/preflight.py
```

Production adds:

```bash
set -a; source ops/.env; set +a
python3 scripts/preflight.py --production
SITE_ENV=production TURNSTILE_SITE_KEY="$TURNSTILE_SITE_KEY" python3 build.py
python3 scripts/qa_static.py --production
```

## Pi 5 install path

Start with `PI5_INSTALL_START_HERE.md`, then use `DEPLOY_PI5.md` for Cloudflare/public production.
