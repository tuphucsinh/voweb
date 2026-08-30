#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 scripts/preflight.py --production
# CMS sync is optional until Directus content replaces file-backed content.
if [[ -n "${DIRECTUS_READ_TOKEN:-}" ]]; then node scripts/sync-directus.mjs || { echo "CMS sync failed; refusing production build"; exit 3; }; fi
SITE_ENV=production TURNSTILE_SITE_KEY="${TURNSTILE_SITE_KEY:?}" python3 build.py
python3 scripts/qa_static.py --production
