# VOrigin — Pi 5 install start here

This release is packaged for **Pi 5 staging first**. Public production remains gated until owner-controlled contact/legal/Cloudflare/approved-market-data items are complete.

## 1. Extract on the Pi

Recommended location:

```bash
mkdir -p ~/projects/vorigin
cd ~/projects/vorigin
# extract the release here
```

## 2. Install the Pi baseline

From the project root:

```bash
sudo ./ops/security/bootstrap-pi5.sh
```

Then **log out and log back in** so Docker group membership takes effect.

Verify:

```bash
docker version
docker compose version || docker-compose version
```

## 3. Generate local secrets

```bash
./scripts/init-pi5-env.sh
```

Save the Directus admin password printed by the script.

## 4. Deploy staging

```bash
./scripts/deploy-pi5.sh staging
```

Verify locally:

```bash
curl -I http://127.0.0.1:8080/vi/
curl http://127.0.0.1:8080/healthz
```

Expected: HTTP success and `ok` from `/healthz`.

## 5. Open the CMS locally/private network

Directus binds only to loopback on the Pi:

```text
http://127.0.0.1:8055
```

Use SSH port forwarding or later Cloudflare Access/Tailscale rather than exposing the port publicly.

## 6. Harden SSH after key login is tested

**Do this only after confirming SSH public-key login works in a second session.**

```bash
sudo ./ops/security/harden-pi5.sh
```

## 7. Cloudflare/public production later

Follow `DEPLOY_PI5.md` and `ops/cloudflare/README.md` to configure:

- `vorigin.vn`
- `www.vorigin.vn`
- `admin.vorigin.vn`
- Cloudflare Tunnel
- Turnstile
- Cloudflare Access for admin

No inbound 80/443 router forwarding is required with the intended Tunnel architecture.

Before public launch:

```bash
set -a; source ops/.env; set +a
python3 scripts/preflight.py --production
```

Production deployment is allowed only when that command returns `PASS`.

## Current release notes

- VI/EN public site and product pages included.
- Latest premium MARIGOLD hero asset integrated.
- Public wording about exclusive Vietnam distribution is intentionally hidden.
- Vitamin/no-preservatives/Halal/manufacturer-quality information remains in public content where supported by the project's current claim registry/source notes.
- `dist/` is built as a preview/noindex build in the package; `deploy-pi5.sh production` rebuilds with production indexing only after preflight passes.
