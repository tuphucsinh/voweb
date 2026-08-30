#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAMP="cms-$(date -u +%Y%m%dT%H%M%SZ)"
REL="/srv/vorigin/releases/$STAMP"
cd "$ROOT"
node scripts/sync-directus.mjs
SITE_ENV=production TURNSTILE_SITE_KEY="${TURNSTILE_SITE_KEY:?}" python3 build.py
python3 scripts/qa_static.py --production
mkdir -p "$REL"
rsync -a --delete dist/ "$REL/"
ln -sfn "$REL" /srv/vorigin/current.next
mv -Tf /srv/vorigin/current.next /srv/vorigin/current
find /srv/vorigin/releases -mindepth 1 -maxdepth 1 -type d -name 'cms-*' -mtime +7 -exec rm -rf {} + || true
curl -fsS http://127.0.0.1:8080/healthz >/dev/null
echo "CMS publish complete: $REL"
