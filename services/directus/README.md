# VOrigin CMS (Directus)

Directus is intentionally private. Bind it to `127.0.0.1:8055` and publish `admin.vorigin.vn` only through Cloudflare Tunnel + Cloudflare Access.

## Bootstrap

1. Start `db` and `directus` with Docker Compose.
2. Export the same `DIRECTUS_ADMIN_EMAIL` / `DIRECTUS_ADMIN_PASSWORD` used in `.env`.
3. Run `node services/directus/bootstrap.mjs`.
4. In Directus Admin create roles:
   - **Admin**: full administration.
   - **Editor**: create/update drafts; no role/permission/admin changes.
   - **Reviewer**: review and publish; no infrastructure settings.
5. Create a static token with **CREATE only** on `leads` for the lead API.
6. Create a separate static token with **READ only** on published `brands/products/pages/insights/claims` for the static build sync job.

Do not give the public visitor role access to CMS collections. The public website is static.
