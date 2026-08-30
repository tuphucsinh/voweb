#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
DEST="${BACKUP_DIR:-/var/backups/vorigin}/$STAMP"
mkdir -p "$DEST"
cp -a "$ROOT/config" "$ROOT/content" "$DEST/"
tar -C "$ROOT" -czf "$DEST/site-dist.tar.gz" dist
if command -v docker >/dev/null 2>&1 && [[ -f "$ROOT/ops/.env" ]]; then
  set -a; source "$ROOT/ops/.env"; set +a
  docker compose --env-file "$ROOT/ops/.env" -f "$ROOT/ops/docker-compose.yml" exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "$DEST/postgres.sql.gz" || true
  docker run --rm -v vorigin_directus_uploads:/src:ro -v "$DEST":/backup alpine sh -c 'tar -C /src -czf /backup/directus-uploads.tar.gz .' || true
fi
find "${BACKUP_DIR:-/var/backups/vorigin}" -mindepth 1 -maxdepth 1 -type d -mtime +30 -exec rm -rf {} + 2>/dev/null || true
if [[ -n "${BACKUP_RSYNC_TARGET:-}" ]]; then rsync -a --delete-delay "$DEST/" "$BACKUP_RSYNC_TARGET/$STAMP/"; fi
echo "Backup complete: $DEST"
