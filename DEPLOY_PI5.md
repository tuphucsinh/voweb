# VOrigin Pi 5 deployment runbook

Do not point public DNS at the Pi until the production preflight passes.

## A. Base OS
Recommended: current 64-bit Raspberry Pi OS / Debian, NVMe-backed filesystem, correct time/NTP, and a non-root admin user.

1. Add and test an SSH public key.
2. Install Tailscale if you want SSH limited to the private mesh.
3. Run `sudo ops/security/harden-pi5.sh` only **after** key login is confirmed.
4. Install Docker + Compose from your preferred maintained Debian/Raspberry Pi source.

## B. Project location

Copy/clone this project on the Pi. Then:

```bash
cp ops/.env.example ops/.env
chmod 600 ops/.env
```

Generate secrets, for example:

```bash
openssl rand -hex 32
```

Use separate random values for DB password, Directus secret, Directus admin password and IP hash salt.

## C. Cloudflare prerequisites

Before production build, create:
- Cloudflare zone for `vorigin.vn`
- Tunnel `vorigin-pi5-prod`
- Turnstile widget for `vorigin.vn` / `www.vorigin.vn`
- Access policy for `admin.vorigin.vn`

Put the Turnstile sitekey/secret in `ops/.env`. The secret must never enter HTML/Git.

See `ops/cloudflare/README.md`.

## D. CMS

```bash
cd ops
# from project root in practice use:
docker compose --env-file .env -f docker-compose.yml up -d db directus lead-api
```

From project root:

```bash
set -a; source ops/.env; set +a
node services/directus/bootstrap.mjs
```

Then configure Directus roles/tokens as described in `services/directus/README.md`.

## E. Site content gates

Edit `config/site.json` with verified company email, phone and address.
Replace prototype logo/MARIGOLD imagery with official authorized assets.
Review `content/claims.json` against the Vietnam import dossier/label.
Review Privacy and Terms.
Only then change the corresponding `launch.*` fields and `production_ready` to true.

## F. Staging on the Pi

Deploying staging uses an isolated root `/srv/vorigin/staging/current`, a dedicated Nginx server block (`ops/nginx/vorigin-staging.conf`), and port `8081`:

```bash
./scripts/deploy-pi5.sh staging
curl -I http://127.0.0.1:8081/vi/
curl -fsS http://127.0.0.1:8081/healthz
```

A staging build is `noindex`.

Staging is static-only and rejects `RUN_DATA_SERVICES=1` because the current Compose stack is shared (`name: vorigin`, shared volumes, and loopback ports `8055`/`8787`). Staging commands cannot restart data services until a physically isolated staging service stack is configured.

## G. Production preflight

```bash
set -a; source ops/.env; set +a
python3 scripts/preflight.py --production
```

This must print `PASS`.

## H. Production deploy

```bash
./scripts/deploy-pi5.sh production
```

The deploy uses a timestamped release and atomically switches `/srv/vorigin/current` serving on loopback port `8080`, making rollback easy.

Static deploys do not restart data services by default (`RUN_DATA_SERVICES=0`). Running data services is an opt-in, separate approved production operation:

```bash
RUN_DATA_SERVICES=1 ./scripts/deploy-pi5.sh production
```

## I. Cloudflare routes

- `vorigin.vn` → `http://127.0.0.1:8080`
- `www.vorigin.vn` → redirect to apex or same origin
- `admin.vorigin.vn` → `http://127.0.0.1:8055` + Access

No inbound home-router port forwarding is required.

## J. Backup + health timers

Copy the provided systemd units to `/etc/systemd/system/`, then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now vorigin-health.timer vorigin-backup.timer
```

Enable `vorigin-content-sync.timer` only after Directus read token and CMS publishing workflow are tested.

## K. Final checks

- `https://vorigin.vn/vi/` and `/en/`
- redirect `www` → apex
- TLS and security headers
- mobile 360/390/430 widths
- contact form + Turnstile
- admin hostname is blocked by Access for unauthorized users
- Search Console / sitemap after launch
- external uptime monitor from a device/service outside the Pi
