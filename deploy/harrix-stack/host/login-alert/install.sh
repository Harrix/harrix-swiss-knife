#!/bin/bash
# Install the password-login Telegram alert on the VPS host (not in Docker).
# Run as root from /opt/harrix-stack. Safe to re-run; keeps the existing config.
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
CONF="/etc/default/harrix-login-alert"

install -m 755 "${SRC}/harrix-login-alert.sh" /usr/local/bin/harrix-login-alert
install -m 644 "${SRC}/harrix-login-alert.service" /etc/systemd/system/harrix-login-alert.service

if [[ ! -f "${CONF}" ]]; then
  cat >"${CONF}" <<'EOF'
# Token from @BotFather
TELEGRAM_BOT_TOKEN=
# Your chat id: message the bot, then run `harrix-login-alert --chat-id`
TELEGRAM_CHAT_ID=
# Name shown in alerts (defaults to the FQDN)
HOST_LABEL=harrix.dev
EOF
fi
chmod 600 "${CONF}"

systemctl daemon-reload
systemctl enable --now harrix-login-alert
systemctl restart harrix-login-alert
systemctl --no-pager --lines=0 status harrix-login-alert | head -n 3
