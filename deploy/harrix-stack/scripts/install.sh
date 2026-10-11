#!/bin/bash
# Install the harrix.dev stack on Ubuntu: Docker Compose (Caddy) + bare Git deploy.
# Run as root after copying deploy/harrix-stack to STACK_DIR. Safe to re-run.
set -euo pipefail

STACK_DIR="${STACK_DIR:-/opt/harrix-stack}"
GIT_DIR="${GIT_DIR:-/var/git/harrix.dev.git}"
WWW_DIR="${WWW_DIR:-/var/www/harrix.dev}"
DOMAIN="${DOMAIN:-harrix.dev}"
CERT_DIR="${STACK_DIR}/certs"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run as root" >&2
  exit 1
fi
if [[ ! -f "${STACK_DIR}/docker-compose.yml" ]]; then
  echo "Missing ${STACK_DIR}/docker-compose.yml" >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive

echo "==> Base packages"
apt-get update -y
apt-get install -y ca-certificates curl git

if ! command -v docker >/dev/null 2>&1; then
  echo "==> Installing Docker Engine + Compose plugin"
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
  # shellcheck disable=SC1091
  . /etc/os-release
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable" \
    >/etc/apt/sources.list.d/docker.list
  apt-get update -y
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
fi
systemctl enable --now docker

NGINX_DUMP=""
if command -v nginx >/dev/null 2>&1; then
  NGINX_DUMP="$(nginx -T 2>/dev/null || true)"
fi

echo "==> TLS certificate (Cloudflare Origin CA)"
mkdir -p "${CERT_DIR}"
chmod 700 "${CERT_DIR}"
if [[ ! -s "${CERT_DIR}/origin.pem" || ! -s "${CERT_DIR}/origin.key" ]]; then
  cert_src="$(printf '%s\n' "${NGINX_DUMP}" | awk '$1=="ssl_certificate"{gsub(";","",$2); print $2; exit}')"
  key_src="$(printf '%s\n' "${NGINX_DUMP}" | awk '$1=="ssl_certificate_key"{gsub(";","",$2); print $2; exit}')"
  if [[ -n "${cert_src}" && -n "${key_src}" && -s "${cert_src}" && -s "${key_src}" ]]; then
    cp "${cert_src}" "${CERT_DIR}/origin.pem"
    cp "${key_src}" "${CERT_DIR}/origin.key"
    echo "Copied ${cert_src} and ${key_src}"
  else
    echo "No certificate found. Put the Cloudflare Origin certificate into" >&2
    echo "  ${CERT_DIR}/origin.pem and ${CERT_DIR}/origin.key, then re-run." >&2
    exit 1
  fi
fi
chmod 600 "${CERT_DIR}/origin.key"

echo "==> Web root ${WWW_DIR}"
mkdir -p "${WWW_DIR}"
if [[ -z "$(ls -A "${WWW_DIR}")" ]]; then
  old_root="$(printf '%s\n' "${NGINX_DUMP}" | awk '$1=="root"{gsub(";","",$2); print $2; exit}')"
  if [[ -n "${old_root}" && -d "${old_root}" && "${old_root}" != "${WWW_DIR}" ]]; then
    cp -a "${old_root}/." "${WWW_DIR}/"
    echo "Copied current site from ${old_root}"
  else
    cp -a "${STACK_DIR}/www-seed/." "${WWW_DIR}/"
    echo "Seeded from www-seed"
  fi
fi

echo "==> Bare Git repository ${GIT_DIR}"
if [[ ! -d "${GIT_DIR}" ]]; then
  mkdir -p "$(dirname "${GIT_DIR}")"
  git init --bare --initial-branch=main "${GIT_DIR}"
fi
install -m 755 "${STACK_DIR}/git/post-receive" "${GIT_DIR}/hooks/post-receive"

if [[ ! -f "${STACK_DIR}/.env" ]]; then
  sed "s/^DOMAIN=.*/DOMAIN=${DOMAIN}/" "${STACK_DIR}/.env.example" >"${STACK_DIR}/.env"
fi

echo "==> Freeing ports 80/443 from host web servers"
for svc in nginx apache2 caddy; do
  if systemctl is-active --quiet "${svc}" 2>/dev/null; then
    systemctl stop "${svc}"
    systemctl disable "${svc}"
    echo "Stopped and disabled ${svc}"
  fi
done

if command -v ufw >/dev/null 2>&1 && ufw status | grep -q "Status: active"; then
  echo "==> ufw: allow SSH/HTTP/HTTPS"
  ufw allow OpenSSH
  ufw allow 80/tcp
  ufw allow 443/tcp
fi

echo "==> Starting stack"
cd "${STACK_DIR}"
docker compose pull caddy
docker compose up -d
docker compose exec -T caddy caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile
docker compose ps

echo
echo "Deploy remote: root@<this-host>:${GIT_DIR}"
echo "Web root:      ${WWW_DIR}"
echo "Rollback:      docker compose -f ${STACK_DIR}/docker-compose.yml down && systemctl enable --now nginx"
