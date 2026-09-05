#!/usr/bin/env bash
set -euo pipefail
MODE="${1:-staging}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ "$MODE" != "staging" && "$MODE" != "production" ]]; then echo "Usage: $0 [staging|production]"; exit 2; fi
if [[ ! -f "$ROOT/ops/.env" ]]; then echo "Missing ops/.env. Copy ops/.env.example and fill secrets first."; exit 2; fi
set -a; source "$ROOT/ops/.env"; set +a

RUN_DATA_SERVICES="${RUN_DATA_SERVICES:-0}"
if [[ "$RUN_DATA_SERVICES" != "0" && "$RUN_DATA_SERVICES" != "1" ]]; then
  echo "RUN_DATA_SERVICES must be 0 or 1"
  exit 2
fi

if [[ "$MODE" == "staging" && "$RUN_DATA_SERVICES" == "1" ]]; then
  echo "RUN_DATA_SERVICES=1 is supported only for production; staging cannot refresh shared data services until an isolated service stack exists."
  exit 2
fi

python3 "$ROOT/scripts/generate_release_manifest.py" --check
(cd "$ROOT" && sha256sum -c CHECKSUMS.sha256)

if [[ "$MODE" == "production" ]]; then
  python3 "$ROOT/scripts/preflight.py" --production
  SITE_ENV=production TURNSTILE_SITE_KEY="${TURNSTILE_SITE_KEY:-}" python3 "$ROOT/build.py"
  python3 "$ROOT/scripts/qa_static.py" --production
else
  SITE_ENV=preview TURNSTILE_SITE_KEY="${TURNSTILE_SITE_KEY:-}" python3 "$ROOT/build.py"
  python3 "$ROOT/scripts/qa_static.py"
fi
python3 "$ROOT/scripts/copy_qa.py"
python3 "$ROOT/scripts/optimize_images.py" --check

DIST_HASHES="$(mktemp)"
DIST_FILE_LIST="$(mktemp)"
REL_FILE_LIST="$(mktemp)"
cleanup() {
  rm -f "$DIST_HASHES" "$DIST_FILE_LIST" "$REL_FILE_LIST"
}
trap cleanup EXIT

(
  cd "$ROOT/dist"
  find . -type f -print | sort > "$DIST_FILE_LIST"
  while IFS= read -r -d '' path; do
    sha256sum -- "$path"
  done < <(find . -type f -print0 | sort -z)
) > "$DIST_HASHES"

if [[ "$RUN_DATA_SERVICES" == "1" ]]; then
  if docker compose version >/dev/null 2>&1; then
    docker compose --env-file "$ROOT/ops/.env" -f "$ROOT/ops/docker-compose.yml" up -d --build db directus lead-api
  elif command -v docker-compose >/dev/null 2>&1; then
    docker-compose --env-file "$ROOT/ops/.env" -f "$ROOT/ops/docker-compose.yml" up -d --build db directus lead-api
  else
    echo "Neither 'docker compose' nor 'docker-compose' is available."
    exit 2
  fi
fi

if [[ "$MODE" == "staging" ]]; then
  APP_ROOT="/srv/vorigin/staging/app"
  RELEASE_ROOT="/srv/vorigin/staging/releases"
  CURRENT_LINK="/srv/vorigin/staging/current"
  NGINX_CONFIG="ops/nginx/vorigin-staging.conf"
  NGINX_SITE="vorigin-staging"
  ORIGIN_PORT="8081"
else
  APP_ROOT="/srv/vorigin/app"
  RELEASE_ROOT="/srv/vorigin/releases"
  CURRENT_LINK="/srv/vorigin/current"
  NGINX_CONFIG="ops/nginx/vorigin.conf"
  NGINX_SITE="vorigin"
  ORIGIN_PORT="8080"
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)-$MODE"
REL="$RELEASE_ROOT/$STAMP"
sudo mkdir -p "$RELEASE_ROOT" "$APP_ROOT"
sudo rsync -a --delete --exclude 'ops/.env' --exclude 'dist' "$ROOT/" "$APP_ROOT/"
sudo mkdir -p "$REL"
sudo rsync -a --delete "$ROOT/dist/" "$REL/"
(
  cd "$REL"
  find . -type f -print | sort > "$REL_FILE_LIST"
)
if ! cmp -s "$DIST_FILE_LIST" "$REL_FILE_LIST"; then
  echo "Release file set differs from built dist."
  exit 2
fi
if ! (cd "$REL" && sha256sum -c "$DIST_HASHES"); then
  echo "Release bytes differ from built dist."
  exit 2
fi
sudo ln -sfn "$REL" "$CURRENT_LINK.next"
sudo mv -Tf "$CURRENT_LINK.next" "$CURRENT_LINK"
sudo cp "$ROOT/$NGINX_CONFIG" "/etc/nginx/sites-available/$NGINX_SITE"
sudo ln -sfn "/etc/nginx/sites-available/$NGINX_SITE" "/etc/nginx/sites-enabled/$NGINX_SITE"
if [[ "$MODE" == "production" ]]; then
  sudo rm -f /etc/nginx/sites-enabled/default
fi
sudo nginx -t
sudo systemctl reload nginx
curl -fsS "http://127.0.0.1:$ORIGIN_PORT/healthz" >/dev/null
printf 'Deployed VOrigin %s release: %s\n' "$MODE" "$REL"
