#!/usr/bin/env bash
set -euo pipefail
if [[ $EUID -ne 0 ]]; then echo "Run with sudo"; exit 1; fi
REAL_USER="${SUDO_USER:-}"
if [[ -z "$REAL_USER" || "$REAL_USER" == "root" ]]; then echo "Run via sudo from your normal admin user"; exit 1; fi
HOME_DIR="$(getent passwd "$REAL_USER" | cut -d: -f6)"
if [[ ! -s "$HOME_DIR/.ssh/authorized_keys" ]]; then
  echo "REFUSING SSH hardening: $REAL_USER has no non-empty authorized_keys. Add and test an SSH key first."; exit 2
fi
apt-get update
apt-get install -y nginx rsync curl ufw fail2ban unattended-upgrades ca-certificates
cat >/etc/ssh/sshd_config.d/99-vorigin-hardening.conf <<CFG
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
X11Forwarding no
AllowUsers $REAL_USER
CFG
sshd -t
systemctl reload ssh || systemctl reload sshd
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
if ip link show tailscale0 >/dev/null 2>&1; then
  ufw allow in on tailscale0 to any port 22 proto tcp
  echo "SSH allowed only on tailscale0."
else
  echo "WARNING: tailscale0 not found. Adding temporary SSH allow rule. Restrict this after Tailscale is installed."
  ufw allow 22/tcp
fi
ufw --force enable
systemctl enable --now fail2ban unattended-upgrades nginx
printf 'server_tokens off;\n' >/etc/nginx/conf.d/99-server-tokens.conf
nginx -t && systemctl reload nginx
echo "Pi hardening baseline applied. Verify a second SSH session before closing the current one."
