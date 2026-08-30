#!/usr/bin/env bash
set -euo pipefail
if [[ $EUID -ne 0 ]]; then echo "Run with sudo"; exit 1; fi
USER_NAME="${SUDO_USER:-}"
if [[ -z "$USER_NAME" || "$USER_NAME" == "root" ]]; then echo "Run via sudo from a normal admin account"; exit 1; fi
apt-get update
apt-get install -y nginx rsync curl ca-certificates git ufw fail2ban unattended-upgrades docker.io
if apt-cache show docker-compose-v2 >/dev/null 2>&1; then apt-get install -y docker-compose-v2; elif apt-cache show docker-compose-plugin >/dev/null 2>&1; then apt-get install -y docker-compose-plugin; else apt-get install -y docker-compose; fi
systemctl enable --now docker nginx fail2ban unattended-upgrades
usermod -aG docker "$USER_NAME"
mkdir -p /srv/vorigin/{app,releases}
mkdir -p /var/backups/vorigin /var/log/vorigin
chown -R "$USER_NAME":"$USER_NAME" /srv/vorigin /var/backups/vorigin /var/log/vorigin
chmod 750 /srv/vorigin /var/backups/vorigin /var/log/vorigin
cat <<MSG
Base packages installed.
IMPORTANT: log out/in before using Docker without sudo because $USER_NAME was added to group docker.
Next: verify SSH key login, then run harden-pi5.sh.
MSG
