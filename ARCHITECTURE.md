# Architecture

```text
Internet
  |
Cloudflare: DNS + TLS + CDN/WAF + Turnstile
  |
Cloudflare Tunnel (outbound-only from Pi)
  |
  +--> vorigin.vn ------> 127.0.0.1:8080 Nginx ---> static /srv/vorigin/current
  |                                  |
  |                                  +--> /api/lead ---> 127.0.0.1:8787 lead-api
  |
  +--> admin.vorigin.vn -> Cloudflare Access -> 127.0.0.1:8055 Directus
                                                   |
                                                PostgreSQL
```

Properties:
- public site survives CMS outages because published content is static
- no database/CMS/API ports are public
- Pi router does not need inbound 80/443 forwarding
- later Pi→Oracle/VPS failover is easy because `dist/` is a self-contained static release
- CMS changes can trigger/poll a static rebuild without making page requests depend on the CMS
