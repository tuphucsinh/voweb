#!/usr/bin/env bash
set -euo pipefail
curl -fsS --max-time 5 http://127.0.0.1:8080/healthz >/dev/null
curl -fsS --max-time 5 http://127.0.0.1:8787/healthz >/dev/null || true
