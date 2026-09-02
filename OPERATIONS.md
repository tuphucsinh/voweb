# VOrigin Operations

## Daily
No manual action should be required. Check alerts if external monitoring is configured.

## Weekly
- review pending CMS drafts/leads
- check free disk space and Pi temperature
- review `journalctl -u nginx` / Docker service status if errors occurred

## Monthly
- install/reboot for pending kernel/security updates when convenient
- verify a backup archive can be listed/read
- review Cloudflare Access members and CMS roles
- review 404s and Search Console coverage

## Quarterly
Perform a restore drill to a temporary directory or spare host. A backup is not considered valid until a restore succeeds.

## Rollback
`/srv/vorigin/releases/` contains timestamped static releases. Point `/srv/vorigin/current` back to the previous release and reload Nginx.

## Caching

- `styles.css` and `app.js` use stable filenames and are served with `expires -1`, so clients revalidate instead of retaining an immutable 30-day copy.
- Images, SVG and favicon assets use a bounded 7-day cache. They are not marked `immutable`; replacing an asset does not require a filename-hash migration in this phase.
- The Nginx asset locations use `expires` rather than nested `add_header Cache-Control`, preserving the server-level security headers through Nginx inheritance.
- After an approved Nginx change, run `nginx -t`, reload only through the approved service path, then verify response headers for `/styles.css`, `/app.js` and one image.


## Failure behavior
If Directus is down, the already-built public site remains online. If the CMS sync fails, the publish script stops before switching the current release. If the lead API is down, only forms are affected; public content remains static.
