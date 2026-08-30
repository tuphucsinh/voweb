# Cloudflare edge setup for VOrigin.vn

Recommended topology:

`visitor → Cloudflare edge (TLS/WAF/CDN) → Cloudflare Tunnel → 127.0.0.1:8080 Nginx on Pi 5`

The Pi does **not** need inbound ports 80/443 opened on the router. Cloudflare Tunnel uses an outbound-only connection.

## DNS / Tunnel

1. Add `vorigin.vn` to Cloudflare and point the registrar nameservers to Cloudflare if not already done.
2. Create a Tunnel named `vorigin-pi5-prod`.
3. Install `cloudflared` on the Pi using Cloudflare's current official package instructions.
4. Run the Tunnel as a system service.
5. Published application routes:
   - `vorigin.vn` → `http://127.0.0.1:8080`
   - `www.vorigin.vn` → `http://127.0.0.1:8080` (or configure an edge redirect to apex)
   - `admin.vorigin.vn` → `http://127.0.0.1:8055`
   - optional `monitor.vorigin.vn` → `http://127.0.0.1:3001`
6. Put **Cloudflare Access** in front of `admin.vorigin.vn` (and monitor if enabled). Allow only authorized identities; require MFA at the identity provider when possible.

## TLS

Use Cloudflare's edge TLS. Set SSL/TLS mode appropriate for Tunnel-managed origins; no public certificate is required on the Pi when the origin is only reached through Tunnel. Force HTTPS at the edge.

After validation, keep HSTS enabled. Do not preload HSTS until the domain/subdomain policy has been tested thoroughly.

## Turnstile

Create a Turnstile widget restricted to `vorigin.vn` and `www.vorigin.vn`.
- public `sitekey` goes into `TURNSTILE_SITE_KEY` during static build.
- secret key goes only into `ops/.env` as `TURNSTILE_SECRET_KEY`.
- server-side Siteverify is mandatory and is already implemented in `services/lead-api/server.mjs`.

## WAF / rate limiting

Recommended edge rules:
- managed WAF rules on the public site.
- stricter rate limiting/challenge on `/api/lead`.
- block obvious scanners from sensitive paths (`/.env`, `/wp-admin`, `/phpmyadmin`, etc.).
- Access policy on `admin.vorigin.vn`; do not rely on a secret URL.

## Cache

Cache static assets aggressively. Avoid caching `/api/*` and the admin hostname. HTML can use Cloudflare cache with conservative purge rules after content rebuilds.
