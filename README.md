# VOrigin Production Platform v1.0.0-rc7-pi5

A production-oriented, Pi-5-ready implementation of the approved VOrigin visual direction.

## What is implemented

- **32 static HTML pages**: complete VI/EN homepage, About, Brands, MARIGOLD, 4 product pages per locale, Capabilities, Partners, Insights, Contact, localised Privacy/Terms, redirects and 404.
- **Locked premium visual system** with mobile/tablet/desktop responsive CSS and the approved subtle `Why Partner → B2B` light-to-dark transition.
- **SEO**: canonical URLs, `hreflang`, meta descriptions, Open Graph, Organization/Product JSON-LD, sitemap, robots and `llms.txt`.
- **Security architecture**: loopback-only Nginx origin, Cloudflare Tunnel design, CSP/HSTS/security headers, UFW/SSH hardening script, private Directus/Postgres, no public database port.
- **Contact/partner lead API** with server-side Turnstile validation, honeypot, field validation, body limits, rate limiting, hashed IP, local durable log and optional Directus/webhook delivery.
- **CMS**: Directus + PostgreSQL Docker Compose, collection bootstrap, draft/review/publish model guidance, private admin via Cloudflare Access.
- **AI admin helper**: draft-only, provider-neutral tool constrained to approved claims. It cannot auto-publish.
- **Ops**: timestamped releases, atomic deploy/rollback model, backup, health checks, systemd timers, logrotate guidance.
- **Content governance**: unconfirmed brands are not shown; product claims have an explicit approval gate.
- **QA**: static link/asset/meta/claim checks; staging builds are noindex.

## Why the public site is static

VOrigin is a corporate/brand/catalogue site. Static generation keeps the public attack surface small, makes the Pi 5 extremely lightly loaded, gives excellent cacheability/performance, and makes later Pi↔VPS failover straightforward.

## Preview

```bash
python3 build.py
python3 scripts/qa_static.py
python3 -m http.server 8080 -d dist
```

Open `http://localhost:8080/vi/` or `/en/`.

## Production blockers still requiring owner-controlled facts/credentials

The code is implemented, but no system can legitimately invent these values:
1. official company phone / physical address (email is already set to `contact@vorigin.vn`);
2. Cloudflare account/Tunnel token and Turnstile keys;
3. official/authorized MARIGOLD production packshots and brand assets;
4. Vietnam-market product claims approved against the actual import dossier/label;
5. reviewed final Privacy/Terms text;
6. Directus admin and service tokens.

Resolved in rc2: official VOrigin Vector Production v4 identity assets are integrated.

`scripts/preflight.py --production` intentionally refuses launch until the corresponding gates are cleared.

## Deploy
Read `DEPLOY_PI5.md`.


## Brand assets — rc2

Official VOrigin Vector Production v4 assets are now integrated for the header, footer and favicon. Full lockups that still contain the former “PURE SOURCE. DEFINED GOALS.” tagline are deliberately not used. See `BRAND_ASSET_AUDIT.md`.

## Premium MAX rc4 pass
- Premium Google Fonts delivery (Cormorant Garamond + Manrope; no font files bundled)
- Higher-resolution approved-concept-derived visual assets
- Full SVG UI icon integration
- Editorial MARIGOLD brand experience and product pages
- Structured capabilities journey and premium partner page
- Mobile art direction using scroll-snap card experiences
- Subtle paper grain, scroll depth and micro-motion
- Contact/Insights/About subpages upgraded to the same visual tier as the homepage

## Bilingual editorial pass — rc5
- Complete Vietnamese and English copy pass across all public pages
- English standardised to International/British usage
- Vietnamese written as natural business Vietnamese rather than literal translation
- Premium tone achieved through restraint, specificity and rhythm rather than luxury adjectives
- AI-style filler/buzzwords removed and governed by `BILINGUAL_COPY_STYLE_GUIDE.md`
- Product and partnership claims remain source-gated
- Equivalent VI/EN language-switch routes across all main and product pages
- See `COPY_AUDIT.md` for checks and editorial decisions


## rc7 Pi 5 release

- Latest premium homepage MARIGOLD hero integrated.
- Public exclusive-distribution wording is intentionally hidden; the internal claim record is retained.
- VI/EN copy and MARIGOLD provenance/product-trust content retained.
- `PI5_INSTALL_START_HERE.md` provides the staging-first install flow.
- Public production remains protected by `preflight.py --production`.
