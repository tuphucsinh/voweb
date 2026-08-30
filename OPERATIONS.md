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

## Failure behavior
If Directus is down, the already-built public site remains online. If the CMS sync fails, the publish script stops before switching the current release. If the lead API is down, only forms are affected; public content remains static.
