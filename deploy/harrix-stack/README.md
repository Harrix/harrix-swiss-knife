# harrix.dev VPS stack

Docker Compose + Git deploy for <https://harrix.dev> (Time4VPS, Ubuntu 24.04, behind Cloudflare).

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [TLS and Cloudflare](#tls-and-cloudflare)
- [Install or update](#install-or-update)
- [HSK settings](#hsk-settings)
- [API (`/api`)](#api-api)
- [Password login alerts](#password-login-alerts)
- [Move to another VPS](#move-to-another-vps)
- [Apps sync (food / fitness / finance)](#apps-sync-food--fitness--finance)

</details>

```text
OnGenerateStaticSite → git push → /var/git/harrix.dev.git → post-receive → /var/www/harrix.dev → Caddy (Docker)
```

| Path on VPS               | Role                                                                      |
| ------------------------- | ------------------------------------------------------------------------- |
| `/opt/harrix-stack`       | This folder: `docker-compose.yml`, `Caddyfile`, `.env`, `certs/`          |
| `/opt/harrix-stack/certs` | Cloudflare Origin CA certificate (`origin.pem`, `origin.key`), not in Git |
| `/var/git/harrix.dev.git` | Bare repo that HSK pushes to                                              |
| `/var/www/harrix.dev`     | Live HTML, mounted read-only into Caddy                                   |

The site is not baked into an image: a push only replaces files, no rebuild.

## TLS and Cloudflare

DNS is proxied through Cloudflare. Caddy serves the Cloudflare Origin CA certificate (SSL mode "Full (strict)") and does not request Let's Encrypt certificates. The Caddyfile trusts Cloudflare edge ranges and reads the visitor IP from `CF-Connecting-IP`, so logs and rate limits see real clients.

Plain HTTP on port 80 serves the site without a redirect, like the previous nginx setup. This keeps the site working if the Cloudflare SSL mode is ever switched to "Flexible" (an origin redirect would loop).

If Cloudflare publishes new ranges (<https://www.cloudflare.com/ips/>), update `trusted_proxies` in `Caddyfile`.

## Install or update

From the HSK repo on Windows, with SSH key access as `root`:

```powershell
powershell -File deploy/harrix-stack/scripts/push-stack.ps1
```

`install.sh` is safe to re-run. On the first run it:

1. Installs Docker Engine and the Compose plugin.
2. Copies the origin certificate and the current web root from the host nginx config.
3. Creates the bare repo with the `post-receive` hook.
4. Stops and disables host nginx, then starts the Caddy container.

Rollback to the old nginx: `docker compose -f /opt/harrix-stack/docker-compose.yml down && systemctl enable --now nginx`.

## HSK settings

`config.json` → `paths_sites[]`:

```json
"deploy_remote": "root@89.40.9.135:/var/git/harrix.dev.git"
```

`git push` runs with `BatchMode=yes`, so the key must work without prompts. `~/.ssh/config`:

```sshconfig
Host harrix-vps 89.40.9.135
  HostName 89.40.9.135
  User root
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
```

Deploy: Site → **Generate static site…** → **Deploy to harrix.dev?**

## API (`/api`)

The `api` service (FastAPI) is off by default. To enable:

1. Uncomment the `handle /api/*` block in `Caddyfile`.
2. `cd /opt/harrix-stack && docker compose --profile api up -d --build && docker compose restart caddy`

Stub endpoints: `GET /api/health`, `GET /api/search?q=…`.

Protection layers for public endpoints:

- Cloudflare in front (WAF, rate limiting rules, "Under Attack" mode).
- Caddy: request body limit (64 KB) and real client IP via `X-Real-IP`.
- FastAPI: SlowAPI per-IP limit (`API_RATE_LIMIT`, default `30/minute`), CORS limited to the site origin.
- The API container has no published port, only Caddy can reach it.

For heavy search later: client-side debounce, cached responses, and a Cloudflare rate limiting rule on `/api/*`.

## Password login alerts

`host/login-alert/` installs a host service (not Docker) that sends a Telegram message on every successful password login: SSH with a password or the Time4VPS Emergency Console. Key-based SSH logins and failed attempts are ignored.

`push-stack.ps1` installs it automatically. One-time setup:

1. In Telegram, create a bot with @BotFather (`/newbot`) and copy the token.
2. Open the new bot and press **Start**.
3. On the VPS: `nano /etc/default/harrix-login-alert`, set `TELEGRAM_BOT_TOKEN=…`.
4. `harrix-login-alert --chat-id` prints your chat ID; set `TELEGRAM_CHAT_ID=…` in the same file.
5. `harrix-login-alert --test`: a test message should arrive.

The config is read on every alert, so no restart is needed. Service logs: `journalctl -u harrix-login-alert`.

## Move to another VPS

1. Copy `/opt/harrix-stack` (with `certs/` and `.env`), `/var/git/harrix.dev.git`, and `/etc/default/harrix-login-alert` to the new host.
2. Run `bash /opt/harrix-stack/scripts/install.sh`.
3. Re-deploy from HSK (or copy `/var/www/harrix.dev`).
4. Switch the Cloudflare DNS record and `deploy_remote` to the new IP.

## Apps sync (food / fitness / finance)

Planned as another service on the same Compose network under `/api/sync/…` with device tokens. Not implemented yet.
