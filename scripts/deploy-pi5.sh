#!/usr/bin/env bash
set -euo pipefail
MODE="${1:-staging}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ "$MODE" != "staging" && "$MODE" != "production" ]]; then echo "Usage: $0 [staging|production]"; exit 2; fi
if [[ ! -f "$ROOT/ops/.env" ]]; then echo "Missing ops/.env. Copy ops/.env.example and fill secrets first."; exit 2; fi
set -a; source "$ROOT/ops/.env"; set +a
if [[ "$MODE" == "production" ]]; then
  python3 "$ROOT/scripts/preflight.py" --production
  SITE_ENV=production TURNSTILE_SITE_KEY="$TURNSTILE_SITE_KEY" python3 "$ROOT/build.py"
  python3 "$ROOT/scripts/qa_static.py" --production
else
  SITE_ENV=preview TURNSTILE_SITE_KEY="${TURNSTILE_SITE_KEY:-}" python3 "$ROOT/build.py"
  python3 "$ROOT/scripts/qa_static.py"
fi
COMPOSE='docker compose'
if ! docker compose version >/dev/null 2>&1; then COMPOSE='docker-compose'; fi
$COMPOSE --env-file "$ROOT/ops/.env" -f "$ROOT/ops/docker-compose.yml" up -d --build db directus lead-api
STAMP="$(date -u +%Y%m%dT%H%M%SZ)-$MODE"
REL="/srv/vorigin/releases/$STAMP"
sudo mkdir -p /srv/vorigin/releases /srv/vorigin/app
sudo rsync -a --delete --exclude 'ops/.env' --exclude 'dist' "$ROOT/" /srv/vorigin/app/
sudo mkdir -p "$REL"
sudo rsync -a --delete "$ROOT/dist/" "$REL/"
sudo ln -sfn "$REL" /srv/vorigin/current.next
sudo mv -Tf /srv/vorigin/current.next /srv/vorigin/current
sudo cp "$ROOT/ops/nginx/vorigin.conf" /etc/nginx/sites-available/vorigin
sudo ln -sfn /etc/nginx/sites-available/vorigin /etc/nginx/sites-enabled/vorigin
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
curl -fsS http://127.0.0.1:8080/healthz >/dev/null
printf 'Deployed VOrigin %s release: %s\n' "$MODE" "$REL"
