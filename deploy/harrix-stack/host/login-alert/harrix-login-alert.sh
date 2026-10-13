#!/bin/bash
# Telegram alert on every successful password login (SSH or console).
# Key-based SSH logins and failed attempts are ignored.
#   harrix-login-alert            follow the journal (systemd service)
#   harrix-login-alert --chat-id  print chat ids of users who messaged the bot
#   harrix-login-alert --test     send a test message and exit
set -uo pipefail

CONF="/etc/default/harrix-login-alert"

# Re-read before each send so edits apply without restarting the service.
load_conf() {
  TELEGRAM_BOT_TOKEN="" TELEGRAM_CHAT_ID="" HOST_LABEL=""
  # shellcheck disable=SC1090
  [[ -f "${CONF}" ]] && source "${CONF}"
  HOST_LABEL="${HOST_LABEL:-$(hostname -f)}"
  API="https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}"
}

require_token() {
  if [[ -z "${TELEGRAM_BOT_TOKEN}" ]]; then
    echo "TELEGRAM_BOT_TOKEN is not set in ${CONF}" >&2
    exit 1
  fi
}

send_message() {
  load_conf
  if [[ -z "${TELEGRAM_BOT_TOKEN}" || -z "${TELEGRAM_CHAT_ID}" ]]; then
    echo "TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is not set in ${CONF}" >&2
    return 1
  fi
  local response
  response="$(curl -sS --max-time 15 --retry 3 --retry-all-errors "${API}/sendMessage" \
    --data-urlencode "chat_id=${TELEGRAM_CHAT_ID}" \
    --data-urlencode "text=$1")" || return 1
  [[ "${response}" == *'"ok":true'* ]] || { echo "Telegram error: ${response}" >&2; return 1; }
}

alert() {
  local kind="$1" user="$2" from="$3" line="$4"
  load_conf
  send_message "$(cat <<EOF
🔐 Password login on ${HOST_LABEL}

Type: ${kind}
User: ${user}
From: ${from}
Time: $(date '+%Y-%m-%d %H:%M:%S %Z')

${line}

Not you? Change the root password (passwd) and check /root/.ssh/authorized_keys and \`last -i\`.
EOF
)" || echo "Failed to send alert for: ${line}" >&2
}

load_conf
case "${1:-}" in
  --chat-id)
    require_token
    curl -sS --max-time 15 "${API}/getUpdates" | python3 -c '
import json, sys
data = json.load(sys.stdin)
if not data.get("ok"):
    sys.exit(f"Telegram error: {data}")
chats = {}
for update in data["result"]:
    chat = (update.get("message") or update.get("my_chat_member") or {}).get("chat")
    if chat:
        chats[chat["id"]] = chat.get("username") or chat.get("first_name") or chat.get("title", "")
if not chats:
    sys.exit("No messages yet: open the bot in Telegram, press Start, then run this again.")
for chat_id, name in chats.items():
    print(chat_id, name)
'
    exit $?
    ;;
  --test)
    send_message "✅ harrix-login-alert test from ${HOST_LABEL}"
    exit $?
    ;;
esac

ssh_re='Accepted (password|keyboard-interactive/pam) for ([^ ]+) from ([^ ]+) port'
console_re='pam_unix\(login:session\): session opened for user ([^ (]+)'

journalctl -f -n 0 -o cat _COMM=sshd + _COMM=sshd-session + _COMM=login | while IFS= read -r line; do
  if [[ "${line}" =~ ${ssh_re} ]]; then
    alert "SSH (${BASH_REMATCH[1]})" "${BASH_REMATCH[2]}" "${BASH_REMATCH[3]}" "${line}"
  elif [[ "${line}" =~ ${console_re} ]]; then
    alert "console (Emergency Console / VNC)" "${BASH_REMATCH[1]}" "local tty" "${line}"
  fi
done
