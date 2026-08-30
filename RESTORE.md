# Restore procedure

1. Provision a clean Pi/VM and install Nginx + Docker/Compose.
2. Restore the project repository to `/srv/vorigin/app` and recreate `ops/.env` from the secure secret copy.
3. Restore PostgreSQL:
   `gunzip -c postgres.sql.gz | docker compose ... exec -T db psql -U "$POSTGRES_USER" "$POSTGRES_DB"`
4. Restore Directus uploads into its Docker volume.
5. Restore or rebuild `dist/` and deploy it as a new timestamped release under `/srv/vorigin/releases/`.
6. Start `db`, `directus`, `lead-api`; reload Nginx.
7. Confirm local `/healthz`, then Cloudflare Tunnel routes and Access.
8. Test a contact submission.

Perform a real restore drill at least quarterly. Keep at least one backup off the Pi/NVMe.
