# API keys

Local secret files for harrix-swiss-knife. **Not committed to Git** (see root `.gitignore`).

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [Files](#files)
  - [GitHub token (optional)](#github-token-optional)
    - [Fine-grained token (preferred)](#fine-grained-token-preferred)
    - [Classic token (alternative)](#classic-token-alternative)
- [Setup](#setup)
- [AI providers](#ai-providers)
- [Transfer to another machine](#transfer-to-another-machine)
- [Installer EXEs and offline snapshots](#installer-exes-and-offline-snapshots)

</details>

## Files

| File                    | Config key                                  | Purpose                                             |
| ----------------------- | ------------------------------------------- | --------------------------------------------------- |
| `pypi-token.txt`        | `pypi_token` in `config/config.json`        | PyPI token for publishing Python libraries          |
| `github-token.txt`      | `github_token` in `config/config.json`      | Optional GitHub PAT for higher API rate limits      |
| `bothub-api-key.txt`    | `bothub_api_key` in `config/config.json`    | BotHub access token for AI features                 |
| `openai-api-key.txt`    | `openai_api_key` in `config/config.json`    | OpenAI API key (chat + Whisper speech)              |
| `anthropic-api-key.txt` | `anthropic_api_key` in `config/config.json` | Anthropic API key (Claude Messages)                 |
| `gemini-api-key.txt`    | `gemini_api_key` in `config/config.json`    | Google Gemini API key                               |
| `ticktick-api-key.txt`  | `ticktick_api_key` in `config/config.json`  | TickTick personal API token (`tp_…`) for habit sync |

AI keys are also read by the Android Gradle build (`android/app/build.gradle.kts`) for the **active** provider from `config.json` → `ai.provider` (override with env). See [`DEVELOPMENT.md`](../DEVELOPMENT.md#ai-api-keys-android).

For school/corporate Wi-Fi, set optional `ai.proxy` (or legacy `bothub.proxy`) in `config/config.json` (see [`DEVELOPMENT.md`](../DEVELOPMENT.md#bothub-food--finance-ai-on-restricted-networks)).

Paths in `config.json` use the `snippet:api-keys/...` prefix; `harrix_pylib` loads file contents at runtime.

### GitHub token (optional)

Used by Dev → **Download ffmpeg, avifenc, avifdec**, **Build installer EXEs** (`hsk dev build-install-zips`), the GUI installer, and related GitHub API calls. Without a token, unauthenticated GitHub REST API is limited to **60 requests/hour per IP**; with a PAT, **5000/hour per account**. Asset zip downloads themselves are not counted in that API quota; the token mainly avoids HTTP 403 when resolving latest releases on shared networks.

1. Copy `github-token.example.txt` → `github-token.txt`.
2. Create a token (form fields below).
3. Paste the token (one line, `github_pat_…` or `ghp_…`). Do not commit the real file.

Override: set env `GITHUB_TOKEN` (takes precedence over the file).

#### Fine-grained token (preferred)

Open [GitHub.com/settings/personal-access-tokens](https://github.com/settings/personal-access-tokens) → **Generate new token**. Or: **Settings → Developer settings → Personal access tokens → Fine-grained tokens**.

On **New fine-grained personal access token** fill the form as follows:

| Field                 | What to set                                                                                                                                                                          |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Token name**        | Any label, for example `for-harrix-swiss-knife`                                                                                                                                      |
| **Description**       | Optional. Example: `Public release downloads for HSK`                                                                                                                                |
| **Resource owner**    | Your GitHub account (not an organization unless you intend that)                                                                                                                     |
| **Expiration**        | `30 days` works; for a personal machine prefer **90 days** or **No expiration** if offered, so downloads do not start failing with 403 after expiry                                  |
| **Repository access** | **Public repositories (read-only)**. Do not choose All repositories or Only select repositories                                                                                      |
| **Permissions**       | Leave empty. Do not click **Add permissions**. Account permissions must stay “No account permissions added yet”. Extra repository permissions (Contents, Metadata, …) are not needed |

Then **Generate token** and copy the value once (`github_pat_…`). GitHub will not show it again.

#### Classic token (alternative)

[GitHub.com/settings/tokens](https://github.com/settings/tokens) → **Generate new token (classic)**. Leave **all scopes unchecked**. Do not enable `repo`, write, or delete. The token starts with `ghp_…`.

## Setup

1. Copy `pypi-token.example.txt` to `pypi-token.txt` (or move an existing token here).
2. Replace the placeholder with your real token (one line, no quotes; PyPI tokens usually start with `pypi-`).
3. Optionally copy `github-token.example.txt` → `github-token.txt` (see above).
4. Do not commit `api-keys/*` except files listed in `.gitignore` exceptions.

Add new keys as separate `.txt` files and reference them from `config.json` with `snippet:api-keys/<filename>`.

## AI providers

Choose the backend in `config/config.json`:

```json
"ai": {
  "provider": "bothub",
  "speech_provider": "",
  "max_image_side": 1600,
  "proxy": ""
}
```

Supported `provider` values: `bothub`, `openai`, `anthropic`, `gemini`.

- `speech_provider` empty means the same as `provider`.
- Anthropic has no speech-to-text API: set `speech_provider` to `openai`, `gemini`, or `bothub` for voice features.
- Copy the matching `*-api-key.example.txt` → `*-api-key.txt` and paste the key (one line).

If `ai` is omitted, the app keeps the previous BotHub-only behavior.

## Transfer to another machine

Personal ZIP (gitignored): secrets from this folder and/or exercise images from `{parent(sqlite_fitness)}/fitness_img` plus the exercise/type catalog from the fitness SQLite database. Workout history (`process`, `weight`) is **not** included. Export checkboxes (or `--api-keys` / `--fitness`) choose which parts to pack. Import overlays `{English name}.avif` next to existing files (does not delete extras) and upserts the catalog by English name without wiping local-only exercises or workouts. Not part of the public install bundles.

Commands (or tray **Dev** → **Transfer private data**):

```text
# Source machine (config.json with real sqlite_fitness required for --fitness)
hsk dev private-data export
# optional: hsk dev private-data export --zip path\to\out.zip
# optional: hsk dev private-data export --api-keys
# optional: hsk dev private-data export --fitness

# Copy install\private-data-harrix-swiss-knife.zip to the new machine

# Target machine: set sqlite_fitness in config.json first; close Fitness tracker if open
hsk dev private-data import
# optional: hsk dev private-data import --zip path\to\in.zip
# optional: hsk dev private-data import --api-keys
# optional: hsk dev private-data import --fitness
```

If the target fitness database file does not exist yet, install creates it from `recover.sql` (base public exercise seed), then upserts the private catalog from the ZIP on top.

## Installer EXEs and offline snapshots

| Artifact                                                                           | Includes `api-keys/`?                                                                                                       |
| ---------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `install/harrix-swiss-knife-online.exe`, `harrix-swiss-knife-offline.exe`          | **No** — only embedded `dependencies/` (not the repo tree).                                                                 |
| `install/dependencies/repos/harrix-swiss-knife.zip` (`git archive HEAD`)           | **No** — whole `api-keys/` is excluded via `.gitattributes` `export-ignore`; secret `*.txt` files are never tracked anyway. |
