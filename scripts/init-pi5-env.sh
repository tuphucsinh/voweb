#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/ops/.env"
EXAMPLE="$ROOT/ops/.env.example"
if [[ -f "$ENV_FILE" ]]; then
  echo "ops/.env already exists; refusing to overwrite it."
  exit 2
fi
cp "$EXAMPLE" "$ENV_FILE"
rand(){ openssl rand -hex 32; }
DB_PASS="$(rand)"
DIRECTUS_SECRET="$(rand)"
DIRECTUS_ADMIN_PASSWORD="$(rand)"
IP_HASH_SALT="$(rand)"
python3 - "$ENV_FILE" "$DB_PASS" "$DIRECTUS_SECRET" "$DIRECTUS_ADMIN_PASSWORD" "$IP_HASH_SALT" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]); vals=sys.argv[2:]
text=p.read_text()
repls={
'POSTGRES_PASSWORD=CHANGE_ME_LONG_RANDOM':'POSTGRES_PASSWORD='+vals[0],
'DIRECTUS_SECRET=CHANGE_ME_LONG_RANDOM':'DIRECTUS_SECRET='+vals[1],
'DIRECTUS_ADMIN_PASSWORD=CHANGE_ME_LONG_RANDOM':'DIRECTUS_ADMIN_PASSWORD='+vals[2],
'IP_HASH_SALT=CHANGE_ME_LONG_RANDOM':'IP_HASH_SALT='+vals[3],
}
for a,b in repls.items(): text=text.replace(a,b)
p.write_text(text)
PY
chmod 600 "$ENV_FILE"
echo "Created $ENV_FILE with random local secrets."
echo "Directus admin email: admin@vorigin.vn"
echo "Directus initial admin password: $DIRECTUS_ADMIN_PASSWORD"
echo
echo "Save the password securely now."
echo "Turnstile/Cloudflare values are intentionally blank for staging and must be added before public production."
