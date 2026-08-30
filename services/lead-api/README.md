# Lead API

Small dependency-free Node service. Public access is only through Nginx `/api/lead`.

Security properties:
- JSON only, 32KB maximum body
- required server-side Cloudflare Turnstile verification
- honeypot
- in-memory per-IP rate limit
- strict field length / format validation
- stores only a salted IP hash, not the raw IP
- always writes a local append-only NDJSON backup
- optional Directus lead sync and optional webhook

Never expose port 8787 publicly. Bind it to `127.0.0.1` in Docker Compose.
