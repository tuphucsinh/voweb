# Security baseline

- Public origin binds to `127.0.0.1:8080`; no router port-forwarding for 80/443.
- Public ingress through Cloudflare Tunnel only.
- `admin.vorigin.vn` protected by Cloudflare Access and CMS credentials.
- SSH keys only; root/password login disabled after key verification.
- UFW default deny inbound; ideally SSH only on Tailscale.
- Directus and lead API bind to loopback; PostgreSQL has no host port.
- Turnstile token is verified server-side.
- Nginx enforces CSP, HSTS, nosniff, frame-ancestors, referrer and permissions policy.
- Secrets live only in `ops/.env`, never Git.
- Automatic OS security updates + fail2ban baseline.
- Daily backups; restore should be tested quarterly.
- Public site is static, limiting the runtime attack surface.

## Secret rotation
Rotate immediately if a secret is exposed: Directus secret/admin password, DB password, Turnstile secret, static tokens, webhook URLs, AI API key.
